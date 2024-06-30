import socket
import struct
import threading

MICAST_GROUP = ('224.1.1.1', 5000)
MTCAST_PORT = 5000
SERVER_ADDRESS = ('', MTCAST_PORT)

class Process:
  def __init__(self, id):
    self.id = id
    self.active = True
    self.leader = None
  
  def __str__(self):
    return f'Process {self.id}'
  
def exchannge_msgs(process , processes):
  print(f'{process} exchange messages.')
  msg = 'Klar?'
  #multicast_client(process, msg)

def receive_messages(sock, client_name):
  while True:
    try:
      data, address = sock.recvfrom(1024)
      print(f'\nMensagem recebida de {address} ({client_name}): {data.decode("utf-8")}')
      msg = 'klar?'
      received_msg = data.decode("utf-8")
      if msg in received_msg:
        multicast_client()
    except socket.timeout:
      continue

def multicast_client(process, msg=''):
  multicast_group = '224.1.1.1'
  server_address = ('', 5000)
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(server_address)

  group = socket.inet_aton(multicast_group)
  mreq = struct.pack('4sL', group, socket.INADDR_ANY)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
  sock.settimeout(1)

  threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

  try:
      while True:
          message = input('Digite uma mensagem para enviar (ou "sair" para encerrar): ')
          if message.lower() == 'sair':
              break

          sock.sendto(message.encode('utf-8'), (multicast_group, 5000))
  finally:
      sock.close()


def main():
  pass

if __name__ == '__main__':
  pName = input('Type process name: ')
  main()