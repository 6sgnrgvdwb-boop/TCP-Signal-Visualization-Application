import numpy as np
from scipy.signal import butter, filtfilt


class SignalProcessor:
    def __init__(self, sampling_rate=1000):
        self.sampling_rate = sampling_rate

        # RMS parameters
        self.rms_window = 100

        # Butterworth filter parameters
        self.low_cut = 20
        self.high_cut = 450
        self.order = 4

    def original(self, signal):
        """
        Returns the original signal.
        """
        return signal

    def rms(self, signal):
        """
        Calculates the RMS signal.
        """

        if len(signal) < self.rms_window:
            return signal

        squared = signal ** 2

        kernel = np.ones(self.rms_window) / self.rms_window

        mean = np.convolve(
            squared,
            kernel,
            mode="same"
        )

        return np.sqrt(mean)

    def filtered(self, signal):
        """
        Butterworth bandpass filter.
        """

        # Avoid filtering very short signals
        if len(signal) < 30:
            return signal

        nyquist = self.sampling_rate / 2

        low = self.low_cut / nyquist
        high = self.high_cut / nyquist

        b, a = butter(
            self.order,
            [low, high],
            btype="band"
        )

        return filtfilt(b, a, signal)

    def process(self, signal, mode):
        """
        Processes the signal based on the selected mode.

        Modes:
            original
            rms
            filtered
        """

        if mode == "original":
            return self.original(signal)

        elif mode == "rms":
            return self.rms(signal)

        elif mode == "filtered":
            return self.filtered(signal)

        return signal