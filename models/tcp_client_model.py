import socket
import numpy as np


class TcpClientModel:
   

    def __init__(
        self,
        host,
        port,
        sampling_rate,
        channels,
        samples_per_packet,
        window_seconds,
        selected_channel,
    ):
        self.host = host
        self.port = port
        self.sampling_rate = sampling_rate
        self.channels = channels
        self.samples_per_packet = samples_per_packet
        self.window_seconds = window_seconds
        self.selected_channel = selected_channel

        self.dtype = np.float64

        self.socket = None
        self.is_connected = False

        self.packet_size = self.channels * self.samples_per_packet
        self.packet_size_bytes = self.packet_size * np.dtype(self.dtype).itemsize

        self.window_size = int(self.sampling_rate * self.window_seconds)

        self.byte_buffer = bytearray()
        self.data_buffer = np.empty((self.channels, 0), dtype=self.dtype)

        self.total_samples_received = 0

    def connect(self):
        """
        Connect to the TCP server.
        """

        if self.is_connected:
            return

        try:
            self.socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM,
            )

            self.socket.connect(
                (self.host, self.port)
            )

            self.socket.setblocking(False)

            self.is_connected = True

        except OSError as error:
            self.socket = None
            self.is_connected = False

            raise ConnectionError(
                f"Could not connect to {self.host}:{self.port}"
            ) from error

    def disconnect(self):
        """
        Close the TCP connection safely.
        """

        self.is_connected = False

        if self.socket is not None:

            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                self.socket.close()
            except OSError:
                pass

            self.socket = None

    def receive_data(self):
        """
        Receive all available TCP data from the server.
        """

        if not self.is_connected or self.socket is None:
            return

        while True:

            try:

                # Read whatever bytes are currently available.
                new_bytes = self.socket.recv(4096)

                if not new_bytes:
                    print("Server closed the connection.")
                    self.disconnect()
                    return

                self.byte_buffer.extend(new_bytes)

            except BlockingIOError:
                break

            except ConnectionResetError:
                print("Connection reset by server.")
                self.disconnect()
                return

            except OSError as error:
                print(f"Socket error: {error}")
                self.disconnect()
                return

        self._extract_packets_from_buffer()

    def _extract_packets_from_buffer(self):
        """
        Convert complete byte packets into NumPy arrays.
        """

        packets = []

        while len(self.byte_buffer) >= self.packet_size_bytes:

            packet_bytes = self.byte_buffer[:self.packet_size_bytes]

            del self.byte_buffer[:self.packet_size_bytes]

            packet = np.frombuffer(
                packet_bytes,
                dtype=self.dtype,
            )

            if packet.size != self.packet_size:
                continue

            packet = packet.reshape(
                self.channels,
                self.samples_per_packet,
            )

            packets.append(packet)

        if len(packets) == 0:
            return

        new_data = np.concatenate(
            packets,
            axis=1,
        )

        self.data_buffer = np.concatenate(
            (self.data_buffer, new_data),
            axis=1,
        )

        self.total_samples_received += new_data.shape[1]

        if self.data_buffer.shape[1] > self.window_size:
            self.data_buffer = self.data_buffer[:, -self.window_size:]

    def has_data(self):
        """Return True if enough data is available for plotting."""
        return self.data_buffer.shape[1] >= 2

    def get_window(self):
        """
        Return x and y data for plotting.
        """

        y = self.data_buffer[self.selected_channel]

        x = np.arange(y.shape[0]) / self.sampling_rate

        return x, y

    def get_signal_time_seconds(self):
        """
        Return the signal time in seconds.
        """

        return self.total_samples_received / self.sampling_rate