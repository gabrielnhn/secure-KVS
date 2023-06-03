#! /bin/python3

import socket

BUFFER_SIZE = 1024  # Tamanho do buffer para receber os dados
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket de cliente
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Define as opções do socket
client.bind(('localhost', 5051))  # Liga o socket de cliente ao localhost e à porta 5051
client.listen()  # Aguarda conexões de entrada
client_conn, addr = client.accept()  # Aceita uma conexão de um cliente

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket de servidor
server.connect(('localhost', 5050))  # Conecta ao servidor

client_conn.settimeout(0.1)
client.settimeout(0.1)
server.settimeout(0.1)

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

def main():

    count = 1
    while True:

        try:
            package = client_conn.recv(BUFFER_SIZE)  # Recebe dados do cliente
            print(f"Mensagem {count} - Cliente enviou:")
            hexdump(package)
        except:
            package = None
      
        if package:
            count += 1
            server.sendall(package)  # Envia os dados modificados para o servidor

        try:
            package = server.recv(BUFFER_SIZE)  # Recebe dados do servidor
            print(f"Mensagem {count} - Servidor enviou:")
            hexdump(package)
        except:
            package = None

        if package:
            count += 1
            client_conn.sendall(package)  # Envia os dados recebidos para o cliente

main()