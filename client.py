import socket
import struct
import threading

def receive_messages(sock, client_name):
    while True:
        try:
            data, address = sock.recvfrom(1024)
            print(f'\nMensagem recebida de {address} ({client_name}): {data.decode("utf-8")}')
            received_msg = data.decode("utf-8")
            teste = received_msg.split(':')
            print(teste[1])
        except socket.timeout:
            continue

def multicast_client(client_name):
    multicast_group = '224.1.1.1'
    server_address = ('', 5000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_address)

    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.settimeout(1)

    threading.Thread(target=receive_messages, args=(sock, client_name), daemon=True).start()

    try:
        while True:
            message = input(f'Digite uma mensagem para enviar como {client_name} (ou "sair" para encerrar): ')
            if message.lower() == 'sair':
                break

            sock.sendto(f'{client_name}:{message}'.encode('utf-8'), (multicast_group, 5000))
    finally:
        sock.close()

if __name__ == "__main__":
    client_name = input("Digite o nome ou ID do cliente: ")
    multicast_client(client_name)
