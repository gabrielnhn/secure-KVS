#! /bin/python3

import socket

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
cliente.bind(('localhost', 5051))
cliente.listen(1)
cliente_conn, addr = cliente.accept()  # Aceita uma conexão de um cliente

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.connect(('localhost', 5050))

cliente_conn.settimeout(0.5)
cliente.settimeout(0.5)
servidor.settimeout(0.5)

def modify_bit(data, bit_index):
    byte_index = bit_index // 8
    bit_offset = bit_index % 8

    byte_data = bytearray(data)
    byte_data[len(byte_data)-1] ^= (1 << bit_offset)

    return bytes(byte_data)

def hexdump(b):
    n = 0
    while n < len(b):
        # Hex string
        s1 = " ".join(f"{i:02x}" for i in b[n : n + 16])
        # Extra space between groups of 8 hex values
        s1 = s1[0:23] + " " + s1[23:]
        # ASCII string, when not in range, output "."
        s2 = "".join(chr(i) if 32 <= i <= 127 else "." for i in b[n : n + 16])

        print(f"{n:08x}: {s1:<48}  {s2}")
        n += 16


def main():
    count = 3

    pacote = cliente_conn.recv(1024)
    servidor.sendall(pacote)

    pacote = servidor.recv(1024)
    cliente_conn.sendall(pacote)

    pacote = servidor.recv(1024)
    cliente_conn.sendall(pacote)

    pacote = cliente_conn.recv(1024)
    servidor.sendall(pacote)

    pacote = servidor.recv(1024)
    cliente_conn.sendall(pacote)

    pacote = servidor.recv(1024)
    cliente_conn.sendall(pacote)

    print("mano")
    while True:

        try:
            pacote = cliente_conn.recv(1024)
            print("Cliente: ")
            hexdump(pacote)
            pacote = modify_bit(pacote, len(pacote) // 2)
            hexdump(pacote)
        except: 
            pacote = None
        
        # print("Recebeu do cliente: ")

        if pacote:
            print("pacotao",pacote)
            servidor.sendall(pacote)

        try:
            pacote = servidor.recv(1024)
            print("Servidor: ")
            hexdump(pacote)
        except: 
            pacote = None
        # print("Recebeu do server: ")

        if pacote:
            cliente_conn.sendall(pacote)

        count += 1

main()