"""These are the settings used by the whole program.

IMPORTANT: SAMPLE_RATE has to match the sampling rate of the Exercise 5
server. It is used for the time axis and for the filter. You can read the
real value from the Exercise 2 recording:
    import pandas as pd
    data = pd.read_pickle("recording.pkl")
    print(data["device_information"]["sampling_frequency"])
"""

# --- TCP server (same format as Exercise 5) ---
HOST = "127.0.0.1"
DEFAULT_PORT = 12345          # the port used in exercise 5

N_CHANNELS = 32
SAMPLES_PER_PACKET = 18
SAMPLE_RATE = 2000

# --- buffers and timing ---
WINDOW_SECONDS = 10          # length of the window in TcpClientmodel
UPDATE_MS = 50               # how often we read from the socket

# --- signal modes---
MODES = {
    "Original": "original",
    "RMS": "rms",
    "Filtered": "filtered",
}

# SignalProcessor.process("rms") uses the raw signal, so the ViewModel filters first when this is True.
RMS_ON_FILTERED = True
