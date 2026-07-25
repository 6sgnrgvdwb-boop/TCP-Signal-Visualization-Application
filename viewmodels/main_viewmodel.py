from PySide6.QtCore import QObject, Signal, QTimer

from models.tcp_client_model import TcpClientModel
from models.signal_buffer import SignalBuffer
from models.signal_processor import SignalProcessor


class MainViewModel(QObject):
    data_updated = Signal(object)
    status_updated = Signal(str)

    def __init__(self):
        super().__init__()

        self.client = None
        self.buffer = SignalBuffer()
        self.processor = SignalProcessor()

        self.current_channel = 0
        self.current_mode = "original"

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

    def connect(self, host, port, sampling_rate=1000):
        try:
            self.client = TcpClient(
                host=host,
                port=port,
                sampling_rate=sampling_rate
            )

            self.client.connect()

            self.timer.start(20)

            self.status_updated.emit("Connected")

        except Exception as e:
            self.status_updated.emit(f"Connection failed: {e}")

    def disconnect(self):
        if self.client:
            self.client.disconnect()

        self.timer.stop()

        self.status_updated.emit("Disconnected")

    def update(self):
        if self.client is None:
            return

        self.client.receive_data()

        if not self.client.has_data():
            return

        self.buffer.buffer = self.client.data_buffer

        signal = self.buffer.get_channel(self.current_channel)

        signal = self.processor.process(
            signal,
            self.current_mode
        )

        self.data_updated.emit(signal)

    def set_channel(self, channel):
        self.current_channel = channel

    def set_mode(self, mode):
        self.current_mode = mode

    def get_all_channels(self):
        return self.buffer.get_all_channels()