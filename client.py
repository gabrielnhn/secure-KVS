#! /bin/python3

import argparse

import socket
import ssl
import json
import logging
import datetime 
import sys

parser = argparse.ArgumentParser(description='Gaze estimation using L2CSNet.')
parser.add_argument(
    '-unsafe', dest='unsafe', help='dont use SSL')
parser.add_argument(
    '-sus', dest='sus', help='I solemly swear that Im up to no good.',
    type=int, default=0)   

args = parser.parse_args()

# Tamanho do buffer
BUFFER_SIZE = 1024

# Definição de constantes de cores para impressão no terminal
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'

# Configuração do log para registrar mensagens em um arquivo
logging.basicConfig(filename='logs/client.log', encoding='utf-8', level=logging.DEBUG)


if args.sus == 0:
    ####### CLIENT LEGIT
    # Cria um contexto padrão
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile="./ssl/server/server.crt")
    # Verifica e carrega certificado
    context.load_cert_chain(certfile = "./ssl/client/client.crt", keyfile = "./ssl/client/client.key")
    context.check_hostname = False


elif args.sus == 1:
    ######### ATTACKER
    # Cria um contexto padrão
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile="./ssl/server/server.crt")
    context.load_cert_chain(certfile = "./ssl/attacker/attacker.crt", keyfile = "./ssl/attacker/attacker.key")
    context.check_hostname = False


else:
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE



HOST = "127.0.0.1"  # O endereço IP ou nome do host do servidor
PORT = 5050 # A porta usada pelo servidor

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

def operation(s):
    # Loop para solicitar a operação a ser executada ao usuário
    while True:
        opcode = input(HEADER + "What operation would you like to do?\n1.Insert\n2.Read"\
                       "\n3.Update\n4.Delete\n5.Close connection\nPlease select a number: ")
        # Utiliza a estrutura "match" para determinar a operação com base no opcode

        if opcode.isdigit() == False:
            print(FAIL + "Please insert a valid operation.\n")
            continue
        
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
                print(WARNING + "Operation not permitted, please try again.\n")

def main():
    is_ssl = True

    if args.unsafe:
        is_ssl = False

    global context
    # Cria o socket do cliente
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        if is_ssl:
            sock = context.wrap_socket(sock, server_hostname = HOST, server_side=False)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Tenta se conectar ao servidor
        try:
            sock.connect((HOST, PORT))
        except ConnectionRefusedError:
            sock.close()
            logging.error(f"{datetime.datetime.now()}: Error: Could not connect to server server")
            exit()
        
        print(OKGREEN + f"Connecting to server on port {PORT}...")
        sock.settimeout(1.0)  # Timeout de 1 segundo

        try:
            data = sock.recv(BUFFER_SIZE)  # Recebe os dados do servidor (buffer de BUFFER_SIZE bytes)
            data = json.loads(data.decode("utf-8"))  # Decodifica os dados
            print(OKBLUE + "------------------------------------")
            print(OKGREEN + "\nServer response: ", data['res'], "\n")
            print(OKBLUE + "------------------------------------")
        except socket.timeout:
            print(FAIL + "No data was received from server, timeout.")
            logging.error(f"{datetime.datetime.now()}: Server timeout.")
        except Exception as e:
            print(f"EXCEPTION {e}")
            sock.close()
            exit()


        # Loop principal do cliente
        while True:
            req = json.dumps(operation(sock))  # Codifica a operação para JSON

            data = req.encode('UTF-8')  # Codifica os dados

            sock.sendall(data)  # Envia os dados codificados pelo socket


            # Espera pela resposta do servidor
            try:
                data = sock.recv(BUFFER_SIZE)  # Recebe os dados do servidor (buffer de BUFFER_SIZE bytes)
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
