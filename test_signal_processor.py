import numpy as np

from models.signal_processor import SignalProcessor

processor = SignalProcessor(sampling_rate=1000)

# Test signal (1000 samples)
signal = np.random.randn(1000)

original = processor.original(signal)
rms = processor.rms(signal)
filtered = processor.filtered(signal)

print("=== Signal Processor Test ===")
print()

print(f"Original shape : {original.shape}")
print(f"RMS shape      : {rms.shape}")
print(f"Filtered shape : {filtered.shape}")

print()

print("First 5 Original values:")
print(original[:5])

print()

print("First 5 RMS values:")
print(rms[:5])

print()

print("First 5 Filtered values:")
print(filtered[:5])

print()

if (
    original.shape == signal.shape
    and rms.shape == signal.shape
    and filtered.shape == signal.shape
):
    print(" SignalProcessor works correctly!")
else:
    print(" SignalProcessor test failed!")