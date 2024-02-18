import socket
import threading
import time

class BasicClient:
    def __init__(self, ipaddr="0.0.0.0", port=8888):
        self.ipaddr = ipaddr
        self.port = port
        self._clt = None

        if not self.ipaddr:
            raise ValueError("IP address is missing or empty")
        if not self.port:
            raise ValueError("Port number is missing")

        self.connect()

    def __del__(self):
        self.stop()

    def stop(self):
        """Close the client connection."""
        if self._clt:
            try:
                self._clt.close()
            except (socket.error, OSError) as e:
                print(f"Error occurred while closing the socket: {e}")
            finally:
                self._clt = None

    def connect(self):
        """Connect to the server."""
        if self._clt:
            return

        addr = (self.ipaddr, self.port)
        self._clt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._clt.connect(addr)
        except (socket.error, OSError) as e:
            self.stop()
            raise ConnectionError(f"Failed to connect to {self.ipaddr}:{self.port}: {e}")

    def send_msg(self, bytes_to_send):
        """Send a message to the server."""
        if not self._clt:
            raise ConnectionError("No connection to server exists")

        buffer = bytearray(1 * 1024 * 1024)  # 1 MB buffer size
        total_bytes = 0
        start_time = time.time()

        try:
            while total_bytes < bytes_to_send * 1024 * 1024 * 1024:
                sent_bytes = self._clt.send(buffer[:min(len(buffer), bytes_to_send * 1024 * 1024 * 1024 - total_bytes)])
                if sent_bytes == 0:
                    raise ConnectionError("Socket connection broken")
                total_bytes += sent_bytes
        except (socket.error, OSError) as e:
            raise ConnectionError(f"Failed to send message to server: {e}")
        finally:
            end_time = time.time()
            print(f"Sent {total_bytes / (1024 * 1024 * 1024)} GB in {end_time - start_time} seconds")
            self.stop()

def run_clients(num_clients, bytes_to_send):
    """Run multiple clients concurrently."""
    threads = []
    for _ in range(num_clients):
        client = BasicClient()
        thread = threading.Thread(target=client.send_msg, args=(bytes_to_send,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    run_clients(num_clients=2, bytes_to_send=20)
