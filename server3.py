import socket
import threading
import time

class BasicServer:
    def __init__(self, ipaddr, port=8888):
        if ipaddr is None:
            raise ValueError("IP address is missing or empty")
        if port is None:
            raise ValueError("Port number is missing")
        if port <= 1024:
            raise ValueError(f"Port number ({port}) must be above 1024")

        self.ipaddr = ipaddr
        self.port = port
        self._svr = None
        self.good = True

    def __del__(self):
        self.stop()

    def stop(self):
        self.good = False
        if self._svr is not None:
            self._svr.close()
            self._svr = None

    def run(self):
        addr = (self.ipaddr, self.port)
        try:
            with socket.create_server(addr) as self._svr:
                self._svr.listen(10)
                print(f"Server ({self.ipaddr}) is listening on {self.port}")

                while self.good:
                    cltconn, caddr = self._svr.accept()
                    print(f"Connection from {caddr[0]}")
                    csession = SessionHandler(cltconn)
                    csession.start()
        except OSError as e:
            if e.errno == socket.errno.EADDRINUSE:
                print(f"Port {self.port} is already in use. Try running the server on a different port.")
            else:
                raise e
        except KeyboardInterrupt:
            print("Server is shutting down gracefully.")
        finally:
            self.stop()


class SessionHandler(threading.Thread):
    def __init__(self, client_connection):
        super().__init__(daemon=False)
        self._cltconn = client_connection
        self.good = True

    def run(self):
        # Receive the message length header (4 bytes)
        length_header = self._cltconn.recv(4)
        if len(length_header) != 4:
            print("Invalid message length header")
            return  # Handle disconnection

        # Extract the message length from the header
        message_length = int.from_bytes(length_header, byteorder='big')

        # Prepare a buffer to receive the data
        buffer = bytearray(message_length)  # 1 MB buffer size
        start_time = time.time()
        total_bytes = 0

        try:
            while self.good:
                chunk = self._cltconn.recv_into(buffer)
                if chunk == 0:
                    break
                total_bytes += chunk
        finally:
            end_time = time.time()
            print(f"Received {total_bytes / (1024 ** 3)} GB")
            print(f"Transfer time: {end_time - start_time} seconds")
            self.close()

    def close(self):
        if self._cltconn is not None:
            try:
                self._cltconn.close()
            except Exception as e:
                print(f"Failed to close client connection: {e}")
            finally:
                self._cltconn = None
                self.good = False


if __name__ == '__main__':
    svr = BasicServer("0.0.0.0", 8888)
    svr.run()
