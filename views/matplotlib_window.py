import numpy as np

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from models.signal_processor import SignalProcessor


class MatplotlibWindow(QMainWindow):
    def __init__(self, channel_data, sampling_rate):
        super().__init__()

        self.channel_data = np.asarray(channel_data)
        self.sampling_rate = sampling_rate
        self.processor = SignalProcessor(sampling_rate)

        self.setWindowTitle("Offline Signal Inspection")
        self.resize(1000, 700)

        self.setup_ui()
        self.connect_signals()
        self.update_plot()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        controls_layout = QHBoxLayout()

        self.channel_combo = QComboBox()
        for channel in range(self.channel_data.shape[0]):
            self.channel_combo.addItem(f"Channel {channel + 1}")

        self.signal_combo = QComboBox()
        self.signal_combo.addItems(["Original", "Filtered", "RMS"])

        controls_layout.addWidget(QLabel("Channel:"))
        controls_layout.addWidget(self.channel_combo)

        controls_layout.addWidget(QLabel("Signal mode:"))
        controls_layout.addWidget(self.signal_combo)

        controls_layout.addStretch()

        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.canvas)

    def connect_signals(self):
        self.channel_combo.currentIndexChanged.connect(self.update_plot)
        self.signal_combo.currentTextChanged.connect(self.update_plot)

    def update_plot(self):
        if self.channel_data.ndim != 2:
            return

        if self.channel_data.shape[1] < 2:
            return

        channel_index = self.channel_combo.currentIndex()
        signal_mode = self.signal_combo.currentText()

        original_signal = self.channel_data[channel_index]

        displayed_signal = self.processor.process(
            original_signal,
            signal_mode.lower()
        )

        time_axis = np.arange(len(displayed_signal)) / self.sampling_rate

        self.ax.clear()
        self.ax.plot(time_axis, displayed_signal)

        self.ax.set_title(
            f"{signal_mode} Signal - Channel {channel_index + 1}"
        )
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.ax.grid(True)

        self.figure.tight_layout()
        self.canvas.draw()