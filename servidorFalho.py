#! /bin/python3

import redis
import json
import socket
import ssl
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
logging.basicConfig(filename='logs/server.log', encoding='utf-8', level=logging.DEBUG)

# Definição do contexto do protocolo SSL para usar o TLS
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

# Verifica e carrega certificado
context.load_verify_locations("ssl/certificate.crt")
context.load_cert_chain("ssl/certificate.crt", "ssl/key.pem")

# Não checa o hostname do assinador do certificado
context.check_hostname = False

HOST = '127.0.0.1'  # Endereço IP para associar o socket
PORT = 5050  # Número da porta para escutar
db = redis.Redis(host=HOST, port=6379, decode_responses=True)

# Função para processar os dados recebidos do cliente
def process_recv(data):
    opcode = int(data['opcode'])
    received_checksum = data.get('checksum', None)
    del data['checksum']  # Remove o campo do checksum dos dados processados
    expected_checksum = calculate_checksum(data)

    if received_checksum != expected_checksum:
        return {"res": "Invalid checksum"}

    # Utiliza a estrutura "match" para determinar a operação com base no opcode
    match opcode:
        case 1:
            # Insere a chave e valor no banco de dados Redis
            db.set(data['key'], data['value'])
            return {"res": "Inserted"}
        case 2:
            # Lê o valor da chave no banco de dados Redis
            value = db.get(data['key'])

            if value == None:
                return {"res": f"Value not found for key {data['key']}"}

            return {"res": value}
        case 3:
            # Atualiza o valor da chave no banco de dados Redis
            oldValue = db.get(data['key'])

            if oldValue == None:
                return {"res": f"Value not found for key {data['key']}"}

            db.delete(data['key'])
            db.set(data['key'], data['value'])
            return {"res": f"Value {oldValue} update to {data['value']}"}
        case 4:
            # Exclui a chave do banco de dados Redis
            value = db.delete(data['key'])

            if value == None:
                return {"res": f"Value not found for key {data['key']}"}

            return {"res": f"Deleted at {data['key']}"}
        case 5:
            logging.info(f"{datetime.datetime.now()}: Closing connection via client.")
            print(OKBLUE + "Received a close connection signal, gracefully stopping.")
            exit(0)
        case _:
            return {"res": "Invalid opcode"}


def calculate_checksum(data):
    checksum = 0

    for key, value in data.items():
        checksum ^= hash(key)
        checksum ^= hash(value)

    return checksum


def main():
    if len(sys.argv) > 1:
        opts = sys.argv[1]

    global context
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket TCP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Define as opções do socket
    sock.bind((HOST, PORT))  # Associa o socket ao endereço IP e porta especificados

    print(OKGREEN + f"Listening on port {PORT}...")
    sock.listen()  # Aguarda por conexões de entrada

    if len(sys.argv) > 1:
        if opts == '-ssl':
            sock = context.wrap_socket(sock, server_side=True)
    conn, addr = sock.accept()  # Aceita uma conexão de um cliente

    with conn:
        logging.info(f"{datetime.datetime.now()}: >>> Server {PORT} connected to client on socket {addr}")
        while True:
            data = conn.recv(1024)  # Recebe dados do cliente (máximo de 1024 bytes)
            data = json.loads(data.decode("utf-8"))  # Decodifica os dados recebidos de bytes para string
            if not data:
                sock.close()  # Fecha o socket
                logging.error(FAIL + "NO connection. Finishing...")
                print("No connection received. Closing.")
                break

            logging.info(f"{datetime.datetime.now()}: Received request {data}")
            response = process_recv(data)
            logging.info(f"{datetime.datetime.now()}: Sending request {json.dumps(response)}")
            conn.sendall(json.dumps(response).encode("utf-8"))  # Envia a resposta de volta para o cliente


if __name__ == "__main__":
    main()
