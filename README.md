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



### TCP Backend

- TCP socket connection
- Byte buffer
- Packet reconstruction
- Rolling buffer (10 seconds)
- float64 data
- 32 channels
- 18 samples per packet