import redis
import socket

HOST = '127.0.0.1'
PORT = 5050

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    print(f"Listening on port {PORT}...")
    s.listen()

    conn, addr = s.accept()

    with conn:
            print(f">>> Server {PORT} connected to client on socket {addr}")
            while True:
                data = conn.recv(1024)
                data = data.decode("utf-8")
                if not data:
                    s.close()
                    print("NO connection. Finishing...")
                    break

                print(f"Received request '{data}'")
                response = "Operation received"
                # do stuff
                conn.sendall(response.encode("utf-8"))

if __name__ == "__main__":
    main()
