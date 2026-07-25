import numpy as np


class SignalBuffer:
    def __init__(self, channels=32, sampling_rate=1000, window_seconds=10):
        self.channels = channels
        self.sampling_rate = sampling_rate
        self.window_seconds = window_seconds

        self.max_samples = sampling_rate * window_seconds

        self.buffer = np.empty((channels, 0), dtype=np.float64)

    def append(self, new_data):
        """
        new_data shape:
        (32, 18)
        """

        self.buffer = np.concatenate(
            (self.buffer, new_data),
            axis=1
        )

        if self.buffer.shape[1] > self.max_samples:
            self.buffer = self.buffer[:, -self.max_samples:]

    def get_channel(self, channel):
        return self.buffer[channel]

    def get_all_channels(self):
        return self.buffer

    def clear(self):
        self.buffer = np.empty((self.channels, 0), dtype=np.float64)

    def has_data(self):
        return self.buffer.shape[1] > 0