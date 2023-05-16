import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 5050  # The port used by the server cache

def main():

    # Create the client socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Try to connect to Cache Server
        try:
            s.connect((HOST, PORT))
        except ConnectionRefusedError:
            s.close()
            print("Error: Could not connect to CACHE server")
            exit()
        
        print(f"Connected to server on port {PORT}...")


        # Client input
        while True:
            req = input(">>> ")

            data = req.encode('UTF-8') # Encode data

            s.sendall(data) # Send encoded data through the socket

            s.settimeout(1.0) # Timeout (1 second)

            # Try to wait for an answer from Cache Server
            try:
                data = s.recv(1024) # Received data from Cache Server (buffer 1024 bytes)
                data = data.decode("utf-8") # Decode data
                print(data)
            except socket.timeout:
                print("No data was received from cache.")
            except:
                s.close()

if __name__ == '__main__':
    main()
