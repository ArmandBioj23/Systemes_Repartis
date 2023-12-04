import socket
import os
import struct
import traceback

def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)

def recv_one_message(sock):
    lengthbuf = recvall(sock, 4)
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

splits = ["/tmp/abiojoux-23/adeployer/splits/S0.txt", "/tmp/abiojoux-23/adeployer/splits/S1.txt", "/tmp/abiojoux-23/adeployer/splits/S2.txt"]

def main():
    """host1 = 'tp-1d23-17.enst.fr'
    host2 = 'tp-5b07-05.enst.fr' # replace with the server IP address or hostname
    host3 = 'tp-1d23-17.enst.fr'
    host4 = 'tp-1d23-17.enst.fr'
    host5 = 'tp-1d23-17.enst.fr'
    hosts = [host1, host2, host3, host4, host5]
    """
    
    port = 51234 # replace with the server port number
    with open('machines.txt', 'r') as f:
        hosts = []
        line = f.readline()
        while line :
            hosts.append(line.strip())
            line = f.readline()
    try:
        clients_socket = []

        for host in hosts : 
            print(host)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            clients_socket.append(client_socket)

        # send "Hello"
        for client_socket in clients_socket:
            message = 'Hello'
            send_one_message(client_socket,message.encode())
            response = recv_one_message(client_socket).decode()
            print(f'Received response: {response}')

        # send "file" 
        for client_socket in clients_socket:
            filename = 'machines.txt'
            filesize = os.path.getsize(filename)
            message = 'file'
            send_one_message(client_socket,message.encode())
            send_one_message(client_socket,filename.encode())
            send_one_message(client_socket,str(filesize).encode())
            with open(filename, 'rb') as f:
                data = f.read(1024)
                while data:
                    send_one_message(client_socket,data)
                    data = f.read(1024)
            response = recv_one_message(client_socket).decode()
            print(f'Received response: {response}')

        # send "Connect"
        for client_socket in clients_socket :
            message = 'Connect'
            send_one_message(client_socket,message.encode())
            response = recv_one_message(client_socket).decode()
            print(f'Received response: {response}')
        
        # send "Go"
        for client_socket in clients_socket :
            message = 'Go'
            send_one_message(client_socket,message.encode())
            response = recv_one_message(client_socket).decode()
            print(f'Received response: {response}')
        
       # send "Map"
        for host in hosts:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try : 
                client_socket.connect((host,port))
                message = 'Map'
                send_one_message(client_socket,message.encode())
                message = splits[hosts.index(host)] 
                send_one_message(client_socket,message.encode())
                response = recv_one_message(client_socket).decode()
                print(f'Received response: {response}')
        
            except Exception as e :
                print("Error")

        print("MAP FINISHED")


        # send "Bye"
        for client_socket in clients_socket :
            message = 'Bye'
            send_one_message(client_socket,message.encode())
            client_socket.close()

    except Exception as e:
        print(f'Error : {e}')
        traceback.print_exc()

if __name__ == '__main__':
    main()