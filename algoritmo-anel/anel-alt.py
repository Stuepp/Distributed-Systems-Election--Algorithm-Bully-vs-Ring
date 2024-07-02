import threading
import time, datetime
from random import randint
import socket
import sys

TCPPORT=8000
UDPPORT=16000
RING = [1, 4, 6, 2, 12, 5, 14, 20, 21, 7, 11, 27, 18, 23, 24, 16, 15, 29, 25, 9]
MAX_PROCESS=int(sys.argv[3])

process_id = int(sys.argv[1])
leader_id = int(sys.argv[2])
status = 'not-elected'

state = "OK"

total_msg = 0

sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

election_dic = {}

def election(caller: int, msg: str, id: int, dir: int):
    global process_id, leader_id, status, total_msg   

    next_id = RING[(RING.index(process_id) + 1) % len(RING)]
    prev_id = RING[RING.index(process_id) - 1] if RING.index(process_id) - 1 >= 0 else RING[MAX_PROCESS - 1]   

    if caller == process_id:
        if msg == 'candidate':
            if id == process_id:
                status = 'elected'
                server_thread = threading.Thread(target=server, daemon=True)
                server_thread.start()
            leader_id = id
            
            m = f"{caller}:elected:{leader_id}:{dir}"
            total_msg += 1
            file = open(f"log/election{process_id}.log", "a")            
            file.write(f"[{datetime.datetime.now()}] {m}\n")
            file.close()

            if dir == 1:
                sender.sendto(m.encode(), ('127.0.0.1', UDPPORT + next_id))
            else:
                sender.sendto(m.encode(), ('127.0.0.1', UDPPORT + prev_id))  
        elif msg == 'elected':
            if id == process_id:
                status = 'elected'
                server_thread = threading.Thread(target=server, daemon=True)
                server_thread.start()
            
            file = open(f"log/election{process_id}.log", "a")
            file.write(f"[{datetime.datetime.now()}] finished election: {leader_id} - total messages:{total_msg}\n")
            file.close()
    else:
        if msg == 'candidate':
            old = election_dic.get(caller, 'erro')
            if old == 'erro':
                election_dic[caller] = id
                new_id = max(process_id, id)
                m = f"{caller}:candidate:{new_id}:{dir}"
                
                total_msg += 1
                file = open(f"log/election{process_id}.log", "a")
                file.write(f"[{datetime.datetime.now()}] {m}\n")
                file.close()

                if dir == 1:
                    sender.sendto(m.encode('utf-8'), ('127.0.0.1', UDPPORT + next_id))
                else:
                    sender.sendto(m.encode('utf-8'), ('127.0.0.1', UDPPORT + prev_id))

            else:
                leader_id = max(old, process_id, id)
                m = f"{caller}:elected:{leader_id}:{-1 if dir == 1 else 1}"
                total_msg += 1

                file = open(f"log/election{process_id}.log", "a")
                file.write(f"[{datetime.datetime.now()}] {m} - total messages: {total_msg}\n")
                file.close()
                
                if dir == 1:
                    sender.sendto(m.encode('utf-8'), ('127.0.0.1', UDPPORT + prev_id))
                else:
                    sender.sendto(m.encode('utf-8'), ('127.0.0.1', UDPPORT + next_id))
        elif msg == 'elected':
            if process_id == id:
                status = 'elected'
                server_thread = threading.Thread(target=server, daemon=True)
                server_thread.start()
            leader_id = id
            m = f"{caller}:elected:{id}:{dir}"
            total_msg += 1

            file = open(f"log/election{process_id}.log", "a")
            file.write(f"[{datetime.datetime.now()}] {m} - total messages: {total_msg}\n")
            file.close()

            if dir == 1:
                sender.sendto(m.encode('utf-8'), ('127.0.0.1', UDPPORT + next_id))
            else:
                sender.sendto(m.encode('utf-8'), ('127.0.0.1', UDPPORT + prev_id))

def start_election():
    global state, total_msg, process_id
    state = 'election'
    next_id = RING[(RING.index(process_id) + 1) % len(RING)]
    prev_id = RING[RING.index(process_id) - 1] if RING.index(process_id) - 1 >= 0 else RING[MAX_PROCESS - 1]

    m1 = f"{process_id}:candidate:{process_id}:{1}"
    m2 = f"{process_id}:candidate:{process_id}:{-1}"

    total_msg += 2
    file = open(f"log/election{process_id}.log", "a")
    file.write(f"[{datetime.datetime.now()}] started election - {m1}/{m2}- total messages:{total_msg}\n")
    file.close()

    sender.sendto(m1.encode('utf-8'), ('127.0.0.1', UDPPORT + next_id))
    sender.sendto(m2.encode('utf-8'), ('127.0.0.1', UDPPORT + prev_id))
    

def task():
    global process_id, leader_id
    time.sleep(randint(2, 3))
    if process_id != leader_id:
        send_to_leader()

def send_to_leader():
    global state
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect(('127.0.0.1', TCPPORT + leader_id))
        s.close()
    except socket.error:
        if state == "OK":
            start_election()

def server():
    try:
        server_sock.bind(('127.0.0.1', TCPPORT + process_id))
        server_sock.listen()
        while True:
            conn, _ = server_sock.accept()
            conn.close()
    except socket.error:
        pass

def receiver():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", UDPPORT + process_id))
    while True:
        data, _ = s.recvfrom(1024)
        msg = data.decode('utf-8').split(':')
        election(int(msg[0]), msg[1], int(msg[2]), int(msg[3]))

if __name__ == "__main__":
    receiver_thread = threading.Thread(target=receiver, daemon=True)
    receiver_thread.start()

    if process_id == leader_id:
        status = 'elected'
        server_thread = threading.Thread(target=server, daemon=True)
        server_thread.start()

    while True:
        if state == "OK":
            task()   