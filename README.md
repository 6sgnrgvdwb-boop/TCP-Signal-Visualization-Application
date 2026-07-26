# TCP Signal Visualization Application - Final Project

A PySide6 desktop application for **live visualization** (VisPy) and
**offline inspection** (Matplotlib) of multi-channel EMG data streamed
over TCP, built with an **MVVM** architecture.

> **Group:** '2'
> 
> | Team member | Responsibility |
> |---|---|
> | 'Rayan Adam' | TCP / backend — `models/` |
> | 'Hemant' | Visualization / frontend — `views/` |
> | 'Yassin Radi' | Documentation / integration — `viewmodels/`, `main.py`, `models/config.py`, README, tooling |



## TCP Backend

- TCP socket connection
- Byte buffer
- Packet reconstruction
- Rolling buffer (10 seconds)
- float64 data
- 32 channels
- 18 samples per packet

## Installation

Needs Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Packages: numpy, scipy, matplotlib, PySide6, vispy.

## Running it

1. Start the TCP server from Exercise 5.
2. Start the application with `python main.py`.
3. Type the port of the server into the *TCP port* field and press
   **Connect**. Streaming starts by itself, **Disconnect** stops it.

`SAMPLE_RATE` in `models/config.py` has to match the sampling rate of the
server, because it is used for the time axis and the filter.

## Live plot (VisPy)

Shows the last 10 seconds of the signal, with the time in seconds on the
x axis.

- **Channel**: which of the 32 channels is shown.
- **Signal mode**: Original, RMS or Filtered.
- **Plot All Channels**: shows all 32 channels at once, drawn with a
  vertical offset so they do not overlap.

## Offline plot (Matplotlib)

After disconnecting, press the button that opens the Matplotlib window to
look at the whole recording. Choose a channel and a signal mode there and
press refresh. You can also show all channels at once. This plot does not
update live, only when you refresh it.

## Signal processing

The parameters come from Exercise 2:

| Mode | What it does |
|---|---|
| Original | nothing, the raw signal |
| Filtered | Butterworth bandpass, order 4, 20-450 Hz, with `filtfilt` |
| RMS | first the bandpass filter, then a moving RMS with a 100 ms window |

The RMS is calculated on the filtered signal, the same order as in
Exercise 2. Filtering first removes the offset, otherwise the RMS mostly shows the baseline 
instead of the signal.

## Project structure (MVVM)

```
main.py                        starts everything and connects the layers

models/                        no GUI code in here
    config.py                  all settings and constants
    signal_processor.py        filter and RMS
    tcp_client_model.py        socket, byte buffer, packet reconstruction


viewmodels/
    main_viewmodel.py          connects the GUI to the models

views/                         only GUI code in here
    main_window.py             main window with the controls
    matplotlib_window.py       offline plot
    vispy_plot_widget.py       live plot

```

The View never talks to the TCP client and never touches the data
directly. It only calls methods on the ViewModel and reacts to its
signals. The models do not know anything about Qt or the GUI. `main.py` is
the only file that knows all three layers.

## Error handling

Errors show a message in the status bar instead of crashing: wrong port,
server not running, connection lost while streaming, and opening the
offline plot before anything was recorded.
