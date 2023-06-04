#! /bin/python3

import socket
import argparse

parser = argparse.ArgumentParser(description="MAN in the middle")
parser.add_argument('-m', dest='modify', help='Should modify bit', type=str, default=True) 
parser.add_argument('-unsafe', dest='unsafe', help='dont use SSL', type=bool, default=False)
args = parser.parse_args()


BUFFER_SIZE = 1024  # Tamanho do buffer para receber os dados
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket de cliente
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Define as opções do socket
client.bind(('localhost', 5051))  # Liga o socket de cliente ao localhost e à porta 5051
print("Listening on port 5051...")
client.listen()  # Aguarda conexões de entrada
client_conn, addr = client.accept()  # Aceita uma conexão de um cliente

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket de servidor
server.connect(('localhost', 5050))  # Conecta ao servidor

# client_conn.settimeout(0.1)
# client.settimeout(0.1)
# server.settimeout(0.1)

def modify_bits(data, index):
    data_bytearray = bytearray(data)
    data_bytearray[index] ^= 1

    return bytes(data_bytearray)

def hexdump(package):
    n = 0
    while n < len(package):
        # String hexadecimal
        s1 = " ".join(f"{i:02x}" for i in package[n : n + 16])
        # Espaço extra entre grupos de 8 valores hexadecimais
        s1 = s1[0:23] + " " + s1[23:]
        # String ASCII, quando estiver fora do intervalo, exibe "."
        s2 = "".join(chr(i) if 32 <= i <= 127 else "." for i in package[n : n + 16])

        print(f"{n:08x}: {s1:<48}  {s2}")
        n += 16

def tls_handshake():
    package = client_conn.recv(BUFFER_SIZE)  # Recebe dados do cliente
    server.sendall(package)  # Envia os dados recebidos para o servidor

    package = server.recv(BUFFER_SIZE)  # Recebe dados do servidor
    client_conn.sendall(package)  # Envia os dados recebidos para o cliente

    package = server.recv(BUFFER_SIZE)  # Recebe dados do servidor
    client_conn.sendall(package)  # Envia os dados recebidos para o cliente

    package = client_conn.recv(BUFFER_SIZE)  # Recebe dados do cliente
    server.sendall(package)  # Envia os dados recebidos para o servidor

    package = client_conn.recv(BUFFER_SIZE)  # Recebe dados do cliente
    server.sendall(package)  # Envia os dados recebidos para o servidor

    package = server.recv(BUFFER_SIZE)  # Recebe dados do servidor
    client_conn.sendall(package)  # Envia os dados recebidos para o cliente

    package = server.recv(BUFFER_SIZE)  # Recebe dados do servidor
    client_conn.sendall(package)  # Envia os dados recebidos para o cliente

    package = server.recv(BUFFER_SIZE)  # Recebe dados do servidor
    client_conn.sendall(package)  # Envia os dados recebidos para o cliente
    
    print("Handshake do TLS concluído.")

def main():

    if not args.unsafe:
        tls_handshake()

    mod = args.modify
    
    package = server.recv(BUFFER_SIZE)  # Recebe dados do servidor
    client_conn.sendall(package)  # Envia os dados recebidos para o cliente

    while True:
        print(f"Should modify == {mod}")

        package = client_conn.recv(BUFFER_SIZE)  # Recebe dados do cliente
        print("Cliente enviou:")
        if not package:
            print("\tNADA")
            exit()
        hexdump(package)

        if mod:
            package = modify_bits(package, (len(package)-5))
            print("Modificado para:")
            hexdump(package)

        print("Enviando para o servidor...")
        server.sendall(package)  # Envia os dados modificados para o servidor

        package = server.recv(BUFFER_SIZE)  # Recebe dados do servidor
        print("Servidor enviou:")
        hexdump(package)

        print("Enviando para o cliente...")
        client_conn.sendall(package)  # Envia os dados recebidos para o cliente


main()
