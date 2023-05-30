#! /bin/python3

import socket
import threading
import ssl

def modify_bit(data, bit_index):
    byte_index = bit_index // 8
    bit_offset = bit_index % 8

    byte_data = bytearray(data)
    byte_data[byte_index] ^= (1 << bit_offset)

    return bytes(byte_data)

def receber_pacote():
    # Cria o socket do servidor
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor_socket.bind(('localhost', 5051))
    servidor_socket.listen(1)
    print('Servidor aguardando conexão...')

    # Aceita a conexão do cliente
    conexao, endereco = servidor_socket.accept()
    print('Conexão estabelecida:', endereco)

    # Cria um contexto SSL para receber os dados
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    conexao_ssl = ssl_context.wrap_socket(conexao, server_side=True)

    # Recebe o pacote do cliente
    pacote = conexao_ssl.recv(1024)
    print('Pacote recebido:', pacote.decode())

    # Fecha a conexão
    conexao_ssl.shutdown(socket.SHUT_RDWR)
    conexao_ssl.close()
    print('Conexão fechada.')

def enviar_pacote(pacote):
    # Cria o socket do cliente
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_socket.connect(('localhost', 5050))

    # Cria um contexto SSL para enviar os dados
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    cliente_ssl = ssl_context.wrap_socket(cliente_socket)

    # Envia o pacote original para o servidor
    cliente_ssl.send(pacote)
    print('Pacote original enviado:', pacote.decode())

    # Modifica o primeiro bit do pacote criptografado
    pacote_modificado = modify_bit(pacote, len(pacote) // 2)

    # Envia o pacote modificado para o servidor
    cliente_ssl.send(pacote_modificado)
    print('Pacote modificado enviado:', pacote_modificado.decode())

    # Fecha a conexão
    cliente_ssl.shutdown(socket.SHUT_RDWR)
    cliente_ssl.close()
    print('Conexão fechada.')

# Inicia a thread para receber o pacote
threading.Thread(target=receber_pacote).start()

# Cria o pacote para enviar pelo cliente
pacote = b'Meu pacote de teste'

# Inicia a thread para enviar o pacote pelo cliente
threading.Thread(target=enviar_pacote, args=(pacote,)).start()
