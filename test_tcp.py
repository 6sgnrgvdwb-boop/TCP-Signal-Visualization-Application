from models.tcp_client_model import TcpClient
import time

client = TcpClient(
    host="127.0.0.1",
    port=5000,          # Falls eure Übung einen anderen Port nutzt, hier anpassen
    sampling_rate=1000
)

client.connect()

print("Connected!")

while True:
    client.receive_data()

    if client.has_data():
        print(client.data_buffer.shape)

    time.sleep(0.02)