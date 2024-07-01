import socket
import struct
import threading
import time
from datetime import datetime

MCAST_GROUP = '224.1.1.1'
PORT = 5000
MCAST_ADDR = ('', PORT)

me = None

class Process:
  def __init__(self, id):
    self.id = id
    self.leaderStatus = False
    self.leader = ''
    self.bullies = []

  def __strt__(self):
    return f'{self.id}'

  def add_bullie(self,bullie):
    self.bullies.append(bullie)
  
  def accept_leader(self,leader):
    self.leader = leader

def is_bullie(sender):
  if sender > me.id and sender not in me.bullies:
    return True
  return False

def who_is_leader(sock, sender, msg):
  if msg == 'King':
    if(sender < me.id):
      election(sock)
  if msg == 'Winner':
    if(sender < me.id):
      election(sock)
    else:
      me.accept_leader(sender)
      me.leaderStatus = True
      print(f'{me.id} my leader is {me.leader}')

def leader_health(sock):
  while True:
    if me.leader != str(me.id):
      time.sleep(3)
      msg = me.leader
      sock.sendto(f'{me.id}:{msg}'.encode('utf-8'), (MCAST_GROUP, 5000))
      me.leaderStatus = False
      time.sleep(1)
      if not me.leaderStatus:
        election(sock)

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
          elif sender < me.id:
            sock.sendto(f'{me.id}:{msg}'.encode('utf-8'), (MCAST_GROUP, 5000))
        
        who_is_leader(sock, sender, msg)

        if msg == me.id:
          msg = 'Gut'
          sock.sendto(f'{me.id}:{msg}'.encode('utf-8'), (MCAST_GROUP, 5000))

        if sender == me.leader and msg == 'Gut':
          me.leaderStatus = True

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
  threading.Thread(target=leader_health, args=(sock,), daemon=True).start()

  try:
    while True:
      if msg == '':
        msg = input(f'\nType "who" to see your leader\nType "el" for election: \nType "sair" to exit or send a msg as {myID}: ')
        if msg.lower() == 'sair':
          break
        if msg.lower() == 'el':
          election(sock)
          msg=''
        if msg.lower() == 'who':
          print(f'{me.id} my leader is {me.leader}')
          msg=''
        else: # não tem uma msg predefinida
          sock.sendto(f'{myID}:{msg}'.encode('utf-8'), (MCAST_GROUP, 5000))
          msg = ''
      else: # já tem uma msg definida, no caso oi, logo tem que se eleger
        sock.sendto(f'{myID}:{msg}'.encode('utf-8'), (MCAST_GROUP, 5000))
        msg = ''
        election(sock)
  finally:
    sock.close()


def election(sock):
  with open('bully.txt', 'a') as file:
    msg = 'King'
    sock.sendto(f'{me.id}:{msg}'.encode('utf-8'), (MCAST_GROUP, 5000))
    
    data_formatada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file.write(f'{me.id};{me.leader};{msg};{data_formatada}\n')
    
    time.sleep(0.5)
    msg = 'Winner'
    sock.sendto(f'{me.id}:{msg}'.encode('utf-8'), (MCAST_GROUP, 5000))
    
    data_formatada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file.write(f'{me.id};{me.leader};{msg};{data_formatada}\n')
    
    me.accept_leader(me.id)
    me.leaderStatus = True
    print(f'{me.id} my leader is {me.leader}')

if __name__ == "__main__":
  me = Process(input("Digite o ID do processo: "))

  mcast_client(me.id, 'oi')