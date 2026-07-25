import numpy as np
from scipy.signal import butter, filtfilt


class SignalProcessor:
    """
    Signal processing methods for the EMG signal.
    """

    def __init__(
        self,
        sampling_rate=1000,
        rms_window=100,
        low_cut=20,
        high_cut=450,
        filter_order=4,
    ):
        self.sampling_rate = sampling_rate
        self.rms_window = rms_window
        self.low_cut = low_cut
        self.high_cut = high_cut
        self.filter_order = filter_order

    def original(self, signal):
        """
        Return the original signal.
        """
        return signal

    def rms(self, signal):
        """
        Root Mean Square using a moving window.
        """

        if len(signal) < self.rms_window:
            return signal

        squared = signal ** 2

        kernel = np.ones(self.rms_window) / self.rms_window

        mean = np.convolve(
            squared,
            kernel,
            mode="same",
        )

        return np.sqrt(mean)

    def filtered(self, signal):
        """
        Butterworth bandpass filter.
        """

        nyquist = self.sampling_rate / 2

        low = self.low_cut / nyquist
        high = self.high_cut / nyquist

        b, a = butter(
            self.filter_order,
            [low, high],
            btype="band",
        )

        return filtfilt(b, a, signal)

    def process(self, signal, mode):
        """
        Select the processing mode.
        """

        if mode == "original":
            return self.original(signal)

        elif mode == "rms":
            return self.rms(signal)

        elif mode == "filtered":
            return self.filtered(signal)

        return signal