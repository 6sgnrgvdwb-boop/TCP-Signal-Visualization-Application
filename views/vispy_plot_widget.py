import numpy as np

from PySide6.QtWidgets import QVBoxLayout, QWidget
from vispy import scene


class VisPyPlotWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = scene.SceneCanvas(
            keys="interactive",
            show=False,
            bgcolor="white",
            size=(1000, 600),
        )

        grid = self.canvas.central_widget.add_grid(margin=10)

        self.y_axis = scene.AxisWidget(
            orientation="left",
            axis_label="Amplitude",
        )
        self.x_axis = scene.AxisWidget(
            orientation="bottom",
            axis_label="Time (s)",
        )

        self.y_axis.width_max = 70
        self.x_axis.height_max = 50

        grid.add_widget(self.y_axis, row=0, col=0)

        self.view = grid.add_view(row=0, col=1)
        self.view.camera = "panzoom"

        grid.add_widget(self.x_axis, row=1, col=1)

        self.x_axis.link_view(self.view)
        self.y_axis.link_view(self.view)

        self.line = scene.Line(
            pos=np.array([[0.0, 0.0], [1.0, 0.0]]),
            color=(0.1, 0.3, 0.8, 1.0),
            parent=self.view.scene,
            width=2,
        )

        self.all_lines = []

        layout.addWidget(self.canvas.native)

    def clear_all_lines(self):
        for line in self.all_lines:
            line.parent = None

        self.all_lines = []

    def update_single_channel(self, x, y):
        x = np.asarray(x)
        y = np.asarray(y)

        if len(x) < 2 or len(y) < 2:
            return

        self.clear_all_lines()

        self.line.parent = self.view.scene
        self.line.set_data(pos=np.column_stack((x, y)))

        y_min = float(np.min(y))
        y_max = float(np.max(y))
        padding = max(0.1, 0.1 * (y_max - y_min))

        self.view.camera.set_range(
            x=(float(np.min(x)), float(np.max(x))),
            y=(y_min - padding, y_max + padding),
        )

    def update_all_channels(self, x, data):
        x = np.asarray(x)
        data = np.asarray(data)

        if len(x) < 2 or data.ndim != 2:
            return

        self.line.parent = None
        self.clear_all_lines()

        offset = np.median(np.ptp(data, axis=1)) * 2

        if offset <= 0 or not np.isfinite(offset):
            offset = 1

        for channel in range(data.shape[0]):
            y = data[channel] + channel * offset
            pos = np.column_stack((x, y))

            line = scene.Line(
                pos=pos,
                color=(0.1, 0.3, 0.8, 1.0),
                parent=self.view.scene,
                width=1,
            )

            self.all_lines.append(line)

        self.view.camera.set_range(
            x=(float(np.min(x)), float(np.max(x))),
            y=(-offset, data.shape[0] * offset),
        )

    def clear_plot(self):
        self.clear_all_lines()
        self.line.parent = self.view.scene
        self.line.set_data(
            pos=np.array([[0.0, 0.0], [1.0, 0.0]])
        )