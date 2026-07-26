"""Starts the application.

This is the only file that knows all three layers. Everything else only
knows its own layer.

The TCP client is not created here, because TcpClientModel needs the port
in its constructor and the port is only known once the user types it in.
MainViewModel creates it in connect_to_server().
"""

import sys

from PySide6.QtWidgets import QApplication

from models import config
from models.signal_processor import SignalProcessor
from viewmodels.main_viewmodel import MainViewModel
from views.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    processor = SignalProcessor(sampling_rate=config.SAMPLE_RATE)
    view_model = MainViewModel(processor)

    window = MainWindow(view_model)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
