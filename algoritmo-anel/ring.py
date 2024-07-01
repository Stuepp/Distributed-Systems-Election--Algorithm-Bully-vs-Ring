import threading
import time
from random import randint
import socket
import sys

RING = [1, 4, 6, 2, 12, 5]

status = 'OK'
total_msg = 0

process_id = int(sys.argv[1])
leader_id = int(sys.argv[2])

port = 12000 + process_id
server_port = 8000 + process_id
sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def server():
    server_sock.bind(('127.0.0.1', server_port))
    server_sock.listen()
    while True:
        conn, _ = server_sock.accept()
        conn.close()

def task():
    process_time = randint(0, 1)
    time.sleep(process_time)
    send_to_leader()

def send_to_leader():
    if process_id != leader_id:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect(('127.0.0.1', 8000 + leader_id))
            s.close()
        except socket.error:
            if status != 'election':
                start_election()

def start_election():
    global status
    global total_msg

    with open(f"log/election{process_id}.log", "a") as file:
        total_msg += 1
        status = 'election'
        next_process = RING[(RING.index(process_id) + 1) % len(RING)]
        file.write(f"Started election - send candidate:{process_id} to {next_process}\n")
        m = f'candidate:{process_id}'.encode('utf-8')
        sender.sendto(m, ('127.0.0.1', 12000 + next_process))

def election(msg, id):
    global status
    global leader_id
    global total_msg

    next_id = RING[(RING.index(process_id) + 1) % len(RING)]
    prev_id = RING[(RING.index(process_id) - 1)]
    
    with open(f'log/election{process_id}.log', 'a') as file:
        if msg == "elected":
            status = 'OK'
            if id == process_id:
                leader_id = process_id
                file.write(f"recv from {prev_id} - {msg}:{id}\n")
                file.write(f"Finished election:{process_id}\n")
                file.write(f"Total messages: {total_msg}\n")

            else:
                leader_id = id
                m = f'elected:{id}'
                file.write(f"recv from {prev_id} - {msg}:{id}\n")
                file.write(f"send to {next_id} - {m}\n")
                total_msg += 1
                file.write(f"Total messages:{total_msg}\n")
                sender.sendto(m.encode('utf-8'), ('127.0.0.1', 12000 + next_id))

        elif process_id != leader_id:
            if msg == "candidate":
                if id == process_id:
                    status = 'OK'
                    leader_id = process_id
                    server_thread = threading.Thread(target=server, daemon=True)
                    server_thread.start()

                    m = f'elected:{process_id}'
                    file.write(f"recv from {prev_id} - {msg}:{id}\n")
                    file.write(f"send to {next_id} - {m}\n")
                    total_msg += 1
                    sender.sendto(m.encode('utf-8'), ('127.0.0.1', 12000 + next_id))

                elif id < process_id:
                    m = 'candidate:{}'.format(process_id)
                    file.write(f"recv from {prev_id} - {msg}:{id}\n")
                    file.write(f"send to {next_id} - {m}\n")
                    total_msg += 1
                    sender.sendto(m.encode('utf-8'), ('127.0.0.1', 12000 + next_id))
                elif id > process_id:

                    m = f'candidate:{id}'
                    file.write(f"recv from {prev_id} - {msg}:{id}\n")
                    file.write(f"send to {next_id} - {m}\n")
                    total_msg += 1
                    sender.sendto(m.encode('utf-8'), ('127.0.0.1', 12000 + next_id))

def receiver():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", port))
    while True:
        data, _ = s.recvfrom(1024)
        msg = data.decode('utf-8').split(':')
        election(msg[0], int(msg[1]))



if __name__ == "__main__":
    receiver_thread = threading.Thread(target=receiver, daemon=True)
    receiver_thread.start()

    if process_id == leader_id:
        server_thread = threading.Thread(target=server, daemon=True)
        server_thread.start()

    while True:
        if status != 'election':
            task()