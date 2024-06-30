import socket
import struct
import threading
import time

MCAST_GROUP = '224.1.1.1'
PORT = 5000
MCAST_ADDR = ('', PORT)

me = None

class Process:
  def __init__(self, id):
    self.id = id
    self.active = True
    self.leader = None
    self.bullies = []

  def __strt__(self):
    return f'{self.id}'

  def add_bullie(self,bullie):
    self.bullies.append(bullie)

def is_bullie(sender):
  if sender > me.id and sender not in me.bullies:
    return True
  return False

def receive_msgs(sock):
  while True:
    try:
      data, address = sock.recvfrom(1024)
      received_msg = data.decode('utf-8')
      received_msg = received_msg.split(':')
      sender = received_msg[0]
      msg = received_msg[1]
      print(f'\n{sender}:{msg}')
      if sender != me.id:
        if msg == 'oi':
          if is_bullie(sender):
            me.add_bullie(sender)
            print(f'{me.id} - {me.bullies}')
          else:
            sock.sendto(f'{me.id}:{msg}'.encode('utf-8'), (MCAST_GROUP, 5000))
        
        if msg == 'King':
          if(sender < me.id):
            election(sock)
        if msg == 'Winner':
          if(sender < me.id):
            election(sock)
          else:
            me.leader = sender
            print(f'{me.id} my leader is {me.leader}')
    except socket.timeout:
      continue

def mcast_client(myID, msg=''):
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(MCAST_ADDR)

  group = socket.inet_aton(MCAST_GROUP)
  mreq = struct.pack('4sL', group, socket.INADDR_ANY)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
  sock.settimeout(1)

  threading.Thread(target=receive_msgs, args=(sock,), daemon=True).start()

  try:
    while True:
      if msg == '':
        msg = input(f'\nType el for election: \nType "sair" to exit or send a msg as {myID}: ')
        if msg.lower() == 'sair':
          break
        if msg.lower() == 'el':
          election(sock)
      else:
        sock.sendto(f'{myID}:{msg}'.encode('utf-8'), (MCAST_GROUP, 5000))
        msg = ''
      
      sock.sendto(f'{myID}:{msg}'.encode('utf-8'), (MCAST_GROUP, 5000))
      msg = ''
  finally:
    sock.close()


def election(sock):
  if me.leader == None:
    msg = 'King'
    sock.sendto(f'{me.id}:{msg}'.encode('utf-8'), (MCAST_GROUP, 5000))
    if me.leader == None:
      msg = 'Winner'
      sock.sendto(f'{me.id}:{msg}'.encode('utf-8'), (MCAST_GROUP, 5000))
      me.leader = me.id

  print(f'{me.id} my leader is {me.leader}')

if __name__ == "__main__":
  me = Process(input("Digite o ID do processo: "))

  mcast_client(me.id, 'oi')