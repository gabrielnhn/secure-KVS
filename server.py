import redis
import json
import socket

HOST = '127.0.0.1'  # IP address to bind the socket to
PORT = 5050  # Port number to listen on
bd = redis.Redis(host='localhost', port=6379, decode_responses=True)

def process_recv(data):
    match int(data['opcode']):
        case 1:
            bd.set(data['key'], data['value'])
            return {"res": "Inserted"}
        case 2:
            value = bd.get(data['key'])
            return {"res": value}
        case 3:
            # oldValue = bd.get(data['key'])
            bd.delete(data['key'])
            bd.set(data['key'], data['value'])
            return {"res": f"Value update to {data['value']}"}
        case 4:
            value = bd.delete(data['key'])
            return {"res": f"Deleted at {data['key']}"}
        case _:
            print("Invalid opcode")
            return {"res": "Invalid opcode"}


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set socket options
    s.bind((HOST, PORT))  # Bind the socket to the specified IP address and port
    print(f"Listening on port {PORT}...")
    s.listen()  # Listen for incoming connections

    conn, addr = s.accept()  # Accept a connection from a client

    with conn:
        print(f">>> Server {PORT} connected to client on socket {addr}")
        while True:
            data = conn.recv(1024)  # Receive data from the client (maximum of 1024 bytes)
            data = json.loads(data.decode("utf-8"))  # Decode the received data from bytes to string
            if not data:
                s.close()  # Close the socket
                print("NO connection. Finishing...")
                break

            print(f"Received request '{data}'")
            response = process_recv(data)
            conn.sendall(json.dumps(response).encode("utf-8"))  # Send the response back to the client

if __name__ == "__main__":
    main()
