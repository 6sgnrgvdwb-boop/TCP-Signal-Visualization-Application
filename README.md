# TCP Signal Visualization Application - Final Project

A PySide6 desktop application for **live visualization** (VisPy) and
**offline inspection** (Matplotlib) of multi-channel EMG data streamed
over TCP, built with an **MVVM** architecture.

> **Group:** '2'
> 
> | Team member | Responsibility |
> |---|---|
> | 'Rayan Adam' | TCP / backend — `models/` |
> | ' ' | Visualization / frontend — `views/` |
> | 'Yassin Radi' | Documentation / integration — `viewmodels/`, `main.py`, `models/config.py`, README, tooling |

## 1. Installation

Requires **Python 3.10+**. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Dependencies (`requirements.txt`): `numpy`, `scipy`, `matplotlib`,
`PySide6`, `vispy`.

> On a minimal Linux system Qt may additionally need the usual X11/OpenGL
> system libraries (`libgl1`, `libegl1`, `libxkbcommon0`, `libxcb-*`).
> On normal desktop installations these are already present.

## 2. Running the application

1. **Start the TCP server from Exercise 5.** It streams packets of
   32 channels × 18 samples of `float64` (`current_window.tobytes()`),
   i.e. 32 × 18 × 8 = **4608 bytes per packet**.

   A byte-compatible **mock server** is included for development and
   testing without the course server:

   ```bash
   python tools/mock_server.py --port 65432
   ```

2. **Start the client:**

   ```bash
   python main.py
   ```

3. **Connect:** enter the server's port in the *TCP port* field (default
   `65432`) and press **Connect**. The status indicator turns green and
   **streaming starts automatically**. **Disconnect** stops the stream.

> ⚠️ **Check `SAMPLE_RATE` in `models/config.py`** — it must match the
> sampling rate of the streamed recording, because it defines the time
> axis, the RMS window length and the filter band. Read the true value
> from the Exercise 2 recording:
>
> ```python
> import pandas as pd
> print(pd.read_pickle("recording.pkl")["device_information"]["sampling_frequency"])
> ```



