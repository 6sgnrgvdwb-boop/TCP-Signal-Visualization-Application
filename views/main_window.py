from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QStatusBar,
)

from models import config
from views.vispy_plot_widget import VisPyPlotWidget
from views.matplotlib_window import MatplotlibWindow


class MainWindow(QMainWindow):
    def __init__(self, view_model):
        super().__init__()

        self.view_model = view_model
        self.offline_window = None

        self.setWindowTitle("TCP Signal Visualization")
        self.resize(1400, 800)

        self.setup_ui()
        self.connect_gui()
        self.connect_viewmodel()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        # ---------------- Left control panel ----------------

        controls = QVBoxLayout()

        controls.addWidget(QLabel("Port"))

        self.port_edit = QLineEdit()
        self.port_edit.setText(str(config.DEFAULT_PORT))
        controls.addWidget(self.port_edit)

        self.connect_button = QPushButton("Connect")
        controls.addWidget(self.connect_button)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setEnabled(False)
        controls.addWidget(self.disconnect_button)

        controls.addSpacing(20)

        controls.addWidget(QLabel("Channel"))

        self.channel_combo = QComboBox()

        for i in range(config.N_CHANNELS):
            self.channel_combo.addItem(f"Channel {i+1}")

        controls.addWidget(self.channel_combo)

        controls.addSpacing(20)

        controls.addWidget(QLabel("Signal mode"))

        self.mode_combo = QComboBox()

        for mode in config.MODES.keys():
            self.mode_combo.addItem(mode)

        controls.addWidget(self.mode_combo)

        controls.addSpacing(20)

        self.plot_all_checkbox = QCheckBox("Plot all channels")
        controls.addWidget(self.plot_all_checkbox)

        self.offline_button = QPushButton("Offline Plot")
        controls.addWidget(self.offline_button)

        controls.addStretch()

        main_layout.addLayout(controls, 1)

        # ---------------- Right plot ----------------

        self.plot = VisPyPlotWidget()

        main_layout.addWidget(self.plot, 5)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def connect_gui(self):
        """
        Connect GUI widgets to the ViewModel.
        """

        self.connect_button.clicked.connect(
            lambda: self.view_model.connect_to_server(
                self.port_edit.text()
            )
        )

        self.disconnect_button.clicked.connect(
            self.view_model.disconnect_from_server
        )

        self.channel_combo.currentIndexChanged.connect(
            self.view_model.set_channel
        )

        self.mode_combo.currentTextChanged.connect(
            self.view_model.set_mode
        )

        self.plot_all_checkbox.toggled.connect(
            self.view_model.set_show_all
        )

        self.offline_button.clicked.connect(
            self.show_offline
        )

    def connect_viewmodel(self):
        """
        Connect ViewModel signals to the GUI.
        """

        self.view_model.status_changed.connect(
            self.status.showMessage
        )

        self.view_model.connection_changed.connect(
            self.connection_changed
        )

        self.view_model.live_single_channel.connect(
            self.plot.update_single_channel
        )

        self.view_model.live_all_channels.connect(
            self.plot.update_all_channels
        )

        self.view_model.offline_data.connect(
            self.open_offline_window
        )

    def connection_changed(self, connected):
        """
        Update buttons depending on connection state.
        """

        self.connect_button.setEnabled(not connected)
        self.disconnect_button.setEnabled(connected)

    def show_offline(self):
        """
        Request the offline plot from the ViewModel.
        """

        self.view_model.show_offline(
            channel=self.channel_combo.currentIndex(),
            mode=self.mode_combo.currentText(),
            all_channels=self.plot_all_checkbox.isChecked(),
        )

    def open_offline_window(self, x, data, title):
        """
        Open a Matplotlib window with the recorded data.
        """

        self.offline_window = MatplotlibWindow(
        x,
        data,
        title,
    )

        self.offline_window.show()

    def closeEvent(self, event):
        """
        Make sure the TCP connection is closed when the GUI exits.
        """

        self.view_model.shutdown()

        if self.offline_window is not None:
            self.offline_window.close()

        event.accept()       