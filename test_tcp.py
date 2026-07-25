from models.tcp_client_model import TcpClientModel
import time

client = TcpClientModel(
    host="127.0.0.1",
    port=5000,
    sampling_rate=1000,
    channels=32,
    samples_per_packet=18,
    window_seconds=10,
    selected_channel=0,
)

client.connect()

print(f"Connected to {client.host}:{client.port}")

try:
    while True:
        client.receive_data()

        if client.has_data():
            print(
                f"Buffer: {client.data_buffer.shape} | "
                f"Time: {client.get_signal_time_seconds():.2f}s"
            )

        time.sleep(0.02)

except KeyboardInterrupt:
    print("\nStopping client...")
    client.disconnect()