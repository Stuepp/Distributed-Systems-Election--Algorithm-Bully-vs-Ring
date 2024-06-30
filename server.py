import socket
import struct

MICAST_GROUP = ('224.1.1.1', 5000)

def multicast_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        while True:
            message = input('Digite uma mensagem para enviar (ou "sair" para encerrar): ')
            if message.lower() == 'sair':
                break

            sock.sendto(message.encode('utf-8'), MICAST_GROUP)
            print('Mensagem enviada para o grupo multicast.')
    finally:
        sock.close()

if __name__ == "__main__":
    multicast_server()
