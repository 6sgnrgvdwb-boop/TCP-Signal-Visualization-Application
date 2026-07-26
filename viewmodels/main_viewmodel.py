"""ViewModel: connects the GUI to the models.

In MVVM the ViewModel is between the View and the Model.
The View calls the methods here (connect_to_server, etc.) and
listens to the signals below. A QTimer reads new data from the socket and
redraws the live plot every UPDATE_MS milliseconds.

Two things I had to work around, because the models were written
before I made the ViewModel:

1. TcpClientModel only keeps the last WINDOW_SECONDS of data, which
   means that it wont work for the offline plot. Therefore, this class
   keeps its own copy of everything that came in in _store_new_samples()

2. SignalProcessor.rms() does not work on a 2d array, because 
   len(signal) is the number of rows (32), which is smaller than its
   window of 100, so it returns the signal unchanged without any RMS.
   That is why _process() always loops over the channels one by one.
"""

import numpy as np
from PySide6.QtCore import QObject, QTimer, Signal

from models import config
from models.tcp_client_model import TcpClientModel


class MainViewModel(QObject):

    # Signals the View listens to
    status_changed = Signal(str)                   # message for the status bar
    connection_changed = Signal(bool)              # True = connected
    live_single_channel = Signal(object, object)   # x, y
    live_all_channels = Signal(object, object)     # x, data (32 rows)
    offline_data = Signal(object, object, str)     # x, data (2D), title

    def __init__(self, processor):
        super().__init__()
        self.processor = processor
        self.client = None          # created te user connects

        # current settings from the GUI
        self.channel = 0           
        self.mode = "Original"  
        self.show_all = False

        # for the offline plotting
        self.recording = []
        self.recorded_samples = 0

        self.timer = QTimer(self)
        self.timer.setInterval(config.UPDATE_MS)
        self.timer.timeout.connect(self.update)

    # At the bottom is what is called when the user clicks on something

    def connect_to_server(self, port_text):
        """Connect to the TCP server and start streaming."""
        if self.client is not None and self.client.is_connected:
            self.status_changed.emit("Already connected.")
            return

        # The port might not be a number, so we must change it
        try:
            port = int(port_text)
        except ValueError:
            self.status_changed.emit(f"'{port_text}' is not a valid port number.")
            return

        # A new connection starts a new recording.
        self.recording = []
        self.recorded_samples = 0

        # TcpClientModel takes the port in its constructor, so we build a new one for every connection
        self.client = TcpClientModel(
            host=config.HOST,
            port=port,
            sampling_rate=config.SAMPLE_RATE,
            channels=config.N_CHANNELS,
            samples_per_packet=config.SAMPLES_PER_PACKET,
            window_seconds=config.WINDOW_SECONDS,
            selected_channel=self.channel,
        )

       
        try:
            self.client.connect()
        except (ConnectionError, OSError) as error:
            self.client = None
            self.status_changed.emit(f"Could not connect: {error}")  # connect() raises ConnectionError if the server is not running.
            return

        self.timer.start()
        self.connection_changed.emit(True)
        self.status_changed.emit(f"Connected to port {port}. Currently running")

    def disconnect_from_server(self):
        """Stop streaming. The recording stays for the offline plot."""
        if self.client is not None:
            self.client.disconnect()
        self.timer.stop()
        self.connection_changed.emit(False)
        seconds = self.recorded_samples / config.SAMPLE_RATE
        self.status_changed.emit(f"Disconnected. {seconds:.1f} s recorded.")

    def set_channel(self, index):
        """Channel dropdown changed (index 0 = Channel 1)"""
        self.channel = index
        if self.client is not None:
            self.client.selected_channel = index

    def set_mode(self, mode):
        """Signal mode dropdown changed. mode is a key of config.MODES."""
        if mode in config.MODES:
            self.mode = mode

    def set_show_all(self, show_all):
        """'Plot All Channels' button was toggled."""
        self.show_all = show_all

    def shutdown(self):
        """Called when the window closes, so nothing keeps running."""
        self.timer.stop()
        if self.client is not None:
            self.client.disconnect()

    # --- runs every UPDATE_MS while streaming ---

    def update(self):
        """Read new data from the socket, then redraw the live plot."""
        if self.client is None:
            return

        # receive_data() handles the byte buffer and the packets itself.
        # It does not raise on errors, it just disconnects, so we check whether the connection is still there afterwards
        self.client.receive_data()

        if not self.client.is_connected:
            self.timer.stop()
            self.connection_changed.emit(False)
            self.status_changed.emit("Connection lost. The recording was kept.")
            return

        self._store_new_samples()

        if not self.client.has_data():
            return

        x, data = self._live_window()

        if self.show_all:
            self.live_all_channels.emit(x, self._process(data))
        else:
            self.live_single_channel.emit(x, self._process(data[self.channel]))

    def _live_window(self):
        """Return (x, data) of the rolling window in TcpClientModel.

        The x axis keeps counting up over the whole session instead of
        restarting at 0, so the live plot scrolls.
        """
        data = self.client.data_buffer
        n = data.shape[1]
        first = self.client.total_samples_received - n
        x = (first + np.arange(n)) / config.SAMPLE_RATE
        return x, data

    def _store_new_samples(self):
        """Keep a copy of everything for the offline plot.

        TcpClientModel throws away everything older than WINDOW_SECONDS,
        so I will copy the new samples out on every timer tick before they get
        lost. We run every 50 ms and the window is 10s, so we can't miss
        anything
        """
        total = self.client.total_samples_received
        new = total - self.recorded_samples

        if new <= 0:
            return

        buffer = self.client.data_buffer
        new = min(new, buffer.shape[1])

        self.recording.append(buffer[:, -new:].copy())
        self.recorded_samples += new

    # --- signal processing ---

    def _process(self, data, mode=None):
        """Apply the selected signal mode.

        Works for one channel (1-D) and for all channels (2-D). For 2D
        data every channel is processed on its own, because
        SignalProcessor.rms() would otherwise return the raw signal.
        """
        mode = self.mode if mode is None else mode
        key = config.MODES[mode]

        if data.ndim == 2:
            return np.vstack([self._process_one(row, key) for row in data])

        return self._process_one(data, key)

    def _process_one(self, signal, key):
        """Process a single channel."""
        if key == "rms" and config.RMS_ON_FILTERED:
            # Exercise 2 filters first and takes the RMS of the filtered signal. .process("rms") uses the raw signal, so we filter here first
            signal = self.processor.process(signal, "filtered")
            return self.processor.process(signal, "rms")

        return self.processor.process(signal, key)

    # --- offline plot using Matplotlib ---

    def show_offline(self, channel, mode, all_channels):
        """Send the whole recording to the Matplotlib window.
        Called when the user presses the refresh button. The offline
        plot only changes when this is called, it does not update live.
        """
        if not self.recording:
            self.status_changed.emit("No data recorded yet. Connect to te tcp and stream first.")
            return

        if mode not in config.MODES:
            self.status_changed.emit(f"Unknown signal mode '{mode}'.")
            return

        data = np.concatenate(self.recording, axis=1)
        x = np.arange(data.shape[1]) / config.SAMPLE_RATE

        if all_channels:
            self.offline_data.emit(
                x, self._process(data, mode), f"All channels [{mode}]"
            )
        else:
            one = data[channel:channel + 1]
            self.offline_data.emit(
                x, self._process(one, mode), f"Channel {channel + 1} [{mode}]"
            )
