#! /bin/python3

import socket
import ssl
import json
import logging
import datetime
import sys

# Definição de constantes de cores para impressão no terminal
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'

# Configuração do log para registrar mensagens em um arquivo
logging.basicConfig(filename='logs/client.log', encoding='utf-8', level=logging.DEBUG)

# Cria um contexto padrão
context = ssl.create_default_context()

# Verifica e carrega certificado
context.load_verify_locations("ssl/certificate.crt")
context.load_cert_chain("ssl/certificate.crt", "ssl/key.pem")

# Não checa o hostname do assinador do certificado
context.check_hostname = False

HOST = "127.0.0.1"  # O endereço IP ou nome do host do servidor
PORT = 5050  # A porta usada pelo servidor

# Funções para cada operação CRUD

def insert():
    key = input("Please select the key to insert: ")
    value = input("Please select the value to insert: ")
    return {"opcode": 1, "key": key, "value": value}

def read():
    key = input("Please select the key (key) to read: ")
    return {"opcode": 2, "key": key}

def update():
    key = input("Please select the key to update: ")
    value = input("Please select the value to update: ")
    return {"opcode": 3, "key": key, "value": value}

def delete():
    key = input("Please select the key (key) to delete: ")
    return {"opcode": 4, "key": key}

def close(s):
    # Registra no log o fechamento da conexão
    logging.info(f"{datetime.datetime.now()}: Closing connection and gracefully stopping.")
    print(OKBLUE + f"Closing connection, bye!")
    data = json.dumps({"opcode": 5}).encode('UTF-8')  # Codifica os dados
    s.sendall(data)  # Envia os dados codificados pelo socket
    exit(0)

def operation(s, fail=False):
    # Loop para solicitar a operação a ser executada ao usuário
    while True:
        opcode = input(HEADER + "What operation would you like to do?\n1.Insert\n2.Read"\
                       "\n3.Update\n4.Delete\n5.Close connection\nPlease select a number: ")
        # Utiliza a estrutura "match" para determinar a operação com base no opcode
        match int(opcode):
            case 1:
                return insert()
            case 2:
                return read()
            case 3:
                return update()
            case 4:
                return delete()
            case 5:
                return close(s)
            case _:
                print(WARNING + "Operation not permitted, please try again.")

def modify_bit(data, bit_index):
    byte_index = bit_index // 8
    bit_offset = bit_index % 8

    byte_data = bytearray(data)
    byte_data[byte_index] ^= (1 << bit_offset)

    return bytes(byte_data)

def main():
    if len(sys.argv) > 1:
        opts = sys.argv[1]

    global context
    # Cria o socket do cliente
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        if len(sys.argv) > 1:
            if opts == '-ssl':
                sock = context.wrap_socket(sock, server_hostname=HOST)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Tenta se conectar ao servidor
        try:
            sock.connect((HOST, PORT))
        except ConnectionRefusedError:
            sock.close()
            logging.error(f"{datetime.datetime.now()}: Error: Could not connect to server server")
            exit()

        print(OKGREEN + f"Connected to server on port {PORT}...")

        fail_enabled = False

        if len(sys.argv) > 2:
            if sys.argv[2] == '-fail':
                fail_enabled = True

        # Loop principal do cliente
        while True:
            req = json.dumps(operation(sock, fail=fail_enabled))  # Codifica a operação para JSON

            data = req.encode('UTF-8')  # Codifica os dados

            if fail_enabled:
                data = modify_bit(data, len(data) // 2)  # Modify the middle bit

            sock.sendall(data)
            sock.settimeout(1.0)  # Timeout de 1 segundo

            # Espera pela resposta do servidor
            try:
                data = sock.recv(1024)  # Recebe os dados do servidor (buffer de 1024 bytes)
                data = json.loads(data.decode("utf-8"))  # Decodifica os dados
                print(OKBLUE + "------------------------------------")
                print(OKGREEN + "\nServer response: ", data['res'], "\n")
                print(OKBLUE + "------------------------------------")
            except socket.timeout:
                print(FAIL + "No data was received from server, timeout.")
                logging.error(f"{datetime.datetime.now()}: Server timeout.")
            except:
                sock.close()

if __name__ == '__main__':
    main()
