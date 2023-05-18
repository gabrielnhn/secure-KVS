import socket
import json

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 5050  # The port used by the server

def insert():
    key = input("Please select the key to insert: ")
    value = input("Please select the value to insert: ")
    return {"opcode": 1, "key": key, "value": value}

def read():
    key = input("Please select the key (key) to read: ")
    return {"opcode": 2, "key": key}

def update():
    key = input("Please select the key to update:")
    value = input("Please select the value to update: ")
    return {"opcode": 3, "key": key, "value": value}

def delete():
    key = input("Please select the key (key) to delete: ")
    return {"opcode": 4, "key": key}


def operation():
    while True:
        opcode = input("What operation would you like to do?\n1.Insert.\n2.Read\n3.Update\n4.Delete\nPlease select a number: ")
        match int(opcode):
            case 1:
                return insert()
            case 2:
                return read()
            case 3:
                return update()
            case 4:
                return delete()
            case _:
                print("Operation not permited, plase try again.")

def main():

    # Create the client socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Try to connect to server Server
        try:
            s.connect((HOST, PORT))
        except ConnectionRefusedError:
            s.close()
            print("Error: Could not connect to server server")
            exit()
        
        print(f"Connected to server on port {PORT}...")


        # Client input
        while True:
            req = json.dumps(operation())

            data = req.encode('UTF-8') # Encode data

            s.sendall(data) # Send encoded data through the socket

            s.settimeout(1.0) # Timeout (1 second)

            # Try to wait for an answer from Server
            try:
                data = s.recv(1024) # Received data from server (buffer 1024 bytes)
                data = json.loads(data.decode("utf-8")) # Decode data
                print(data['res'])
            except socket.timeout:
                print("No data was received from server.")
            except:
                s.close()

if __name__ == '__main__':
    main()
