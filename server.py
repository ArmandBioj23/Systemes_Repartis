import socket
import threading
import struct
import traceback
import re
import time
from itertools import dropwhile # Permet de créer un générateur qui ignore les éléments d'une séquence tant qu'une condition spécifiée est vraie, puis renvoie tous les éléments restants  

UNAVAIBLE_CHAR = "!|\(|\)|\{|\}|\||:|\?|;| |,|\.|\n|'|/|<|>|="

map_list = [] 

def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)

def recv_one_message(sock):
    lengthbuf = recvall(sock, 4)
    if not lengthbuf:
        return ''
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)

def recvall(sock, count):
    fragments = []
    while count: 
        chunk = sock.recv(count)
        if not chunk: 
            return None
        fragments.append(chunk)
        count -=len(chunk)
    arr = b''.join(fragments)
    return arr

def map_repartition(mot):
    with open("machines.txt", 'r', encoding='utf-8') as file:
        ips = [line.strip() for line in file]
        machine = hash(mot) % len(ips)
        ips = sorted(ips)
        return ips[machine]

def mapping(split):
    file = split
    with open(file, 'r', encoding='utf-8') as file:
        for line in file:
            words = line.split()
            for word in words:
                word = word.strip('.,!?":;()[]{}')
                word = word.lower()
                map_list.append(word)


def handle_client(client_socket, address):
    print(f'{socket.gethostname()} New client connected: {address}')
    try:
        while True:
            data = recv_one_message(client_socket)
            if not data:
                break
            message = data.decode().strip().lower() # convert message to lowercase
            print(f'{socket.gethostname()} Received message from {address}: {message}')
            if message == 'hello':
                response = f'Hello {address}'
                send_one_message(client_socket,response.encode())
            elif message == 'file':
                # receive filename
                filename = recv_one_message(client_socket).decode().strip()
                print(f'{socket.gethostname()} Received filename from {address}: {filename}')

                # receive filesize
                filesize = int(recv_one_message(client_socket).decode().strip())
                print(f'{socket.gethostname()} Received filesize from {address}: {filesize}')

                # receive file data
                with open(filename, 'wb') as f:
                    remaining_bytes = filesize
                    while remaining_bytes > 0:
                        data = recv_one_message(client_socket)
                        if not data:
                            break
                        f.write(data)
                        remaining_bytes -= len(data)
                print(f'{socket.gethostname()} Received the entire file from {address}: {filesize}')
                response = "file received"
                send_one_message(client_socket,response.encode())
                
            elif message == "connect" :
               # read file and connect to other workers 
                with open(filename, 'r') as f:
                    workers = []
                    line = f.readline()
                    while line :
                        # print(line)
                        workers.append(line.strip())
                        line = f.readline()
                clients_socket = []
                for worker in workers :
                        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        client.connect((worker, port))
                        clients_socket.append(client)
                response = 'accepted'
                send_one_message(client_socket,response.encode())

            elif message == 'go' :
                i = 0
                for client in clients_socket :
                    if client != socket.gethostname() :
                        message = 'hello'
                        send_one_message(client,message.encode())
                        response = recv_one_message(client).decode()
                        print(f'Received response: {response}')
                response = 'hello send'
                send_one_message(client_socket,response.encode())

            elif message == 'map' :
                filename = recv_one_message(client_socket).decode().strip()

                with open(filename, 'r', encoding="utf-8") as file:
                    for line in file:
                        words = line.split()
                        for word in words:
                            word = word.strip('.,!?":;()[]{}')
                            word = word.lower()
                            map_list.append(word)
                            print(map_list)
            
                response = 'map finished'
                send_one_message(client_socket,response.encode())

            elif message == 'shuffle'

            elif message == 'bye':
                break
    except Exception as e:
        print(f'{socket.gethostname()} Error handling client {address}: {e}')
        traceback.print_exc()
    finally:
        client_socket.close()
        print(f'{socket.gethostname()} Client disconnected: {address}')

def start_server(port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen()
        print(f'{socket.gethostname()} Server listening on port {port}')

        while True:
            client_socket, address = server_socket.accept()
            print(f'{socket.gethostname()} Accepted new connection from {address}')
            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.start()
    except Exception as e:
        print(f'{socket.gethostname()} Error starting server: {e}')
        traceback.print_exc()
    finally:
        server_socket.close()

if __name__ == '__main__':
    port = 51234 # pick any free port you wish that is not used by other students
    start_server(port)