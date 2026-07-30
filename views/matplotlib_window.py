import numpy as np

from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.figure import Figure


class MatplotlibWindow(QMainWindow):
    def __init__(self, x, data, title):
        super().__init__()

        self.x = np.asarray(x)
        self.data = np.asarray(data)
        self.title = title

        # Convert one channel from 1-D to the same 2-D format
        # used for multiple channels.
        if self.data.ndim == 1:
            self.data = self.data.reshape(1, -1)

        number_of_channels = self.data.shape[0]
        number_of_samples = self.data.shape[1]

        self.plot_information = (
            f"Channels: {number_of_channels} | "
            f"Samples: {number_of_samples}"
        )

        self.setWindowTitle(title)
        self.resize(1000, 700)

        self.setup_ui()
        self.update_plot()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.info_label = QLabel(
            f"{self.plot_information} | "
            "Use the toolbar to zoom, pan, or save the plot."
        )

        self.redraw_button = QPushButton("Redraw Plot")
        self.redraw_button.clicked.connect(self.update_plot)

        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.ax = self.figure.add_subplot(111)

        layout.addWidget(self.info_label)
        layout.addWidget(self.redraw_button)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, 1)

    def update_plot(self):
        if self.data.ndim != 2:
            return

        if self.data.shape[1] < 2:
            return

        if len(self.x) != self.data.shape[1]:
            return

        self.ax.clear()

        if self.data.shape[0] == 1:
            self.plot_single_channel()
        else:
            self.plot_all_channels()

        self.ax.set_title(self.title)
        self.ax.set_xlabel("Time (s)")
        self.ax.grid(True)

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_single_channel(self):
        signal = self.data[0]

        self.ax.plot(
            self.x,
            signal,
            linewidth=1,
        )

        self.ax.set_ylabel("Amplitude")

    def plot_all_channels(self):
        channel_ranges = np.ptp(self.data, axis=1)
        offset = np.median(channel_ranges) * 2

        if offset <= 0 or not np.isfinite(offset):
            offset = 1

        tick_positions = []
        tick_labels = []

        for channel in range(self.data.shape[0]):
            shifted_signal = (
                self.data[channel]
                + channel * offset
            )

            self.ax.plot(
                self.x,
                shifted_signal,
                linewidth=0.8,
            )

            tick_positions.append(channel * offset)
            tick_labels.append(str(channel + 1))

        self.ax.set_ylabel("Channel")
        self.ax.set_yticks(tick_positions)
        self.ax.set_yticklabels(tick_labels)