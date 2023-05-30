#! /bin/python3

import socket

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
cliente.bind(('localhost', 5051))
cliente.listen(1)
cliente_conn, addr = cliente.accept()  # Aceita uma conexão de um cliente
cliente_conn.settimeout(0.1)
cliente.settimeout(0.1)

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.connect(('localhost', 5050))
servidor.settimeout(0.1)

def modify_bit(data, bit_index):
    byte_index = bit_index // 8
    bit_offset = bit_index % 8

    byte_data = bytearray(data)
    byte_data[byte_index] ^= (1 << bit_offset)

    return bytes(byte_data)

def main():
    count = 3
    while True:

        try:
            pacote = cliente_conn.recv(1024)

            if count % 9 == 0:
                pacote = modify_bit(pacote, 5)
        except: 
            pacote = None
        print("Recebeu do cliente: ")

        if pacote:
            servidor.sendall(pacote)

        try:
            pacote = servidor.recv(1024)
        except: 
            pacote = None
        print("Recebeu do server: ")

        if pacote:
            cliente_conn.sendall(pacote)

        count += 1

main()