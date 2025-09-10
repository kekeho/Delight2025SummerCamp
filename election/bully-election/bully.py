import threading
from enum import Enum
import json
import socket
from typing import List, Optional
import time



ELECTION = 1
OK = 2
COORDINATOR = 3
PING = 4  # Alive?
PONG = 5  # Yes


class Message():
    message_type: int
    sender: int

    def __init__(self, message_type: int, sender: int):
        self.message_type = message_type
        self.sender = sender
    
    def to_json_bytes(self) -> bytes:
        s = json.dumps({
            "message_type": int(self.message_type),
            "sender": self.sender
        })
        return s.encode("utf-8")

    @staticmethod
    def from_json_bytes(bytes: bytes) -> Optional["Message"]:
        s = bytes.decode("utf-8")
        d = json.loads(s)
        try:
            message_type = d["message_type"]
            sender = d["sender"]
            if type(message_type) != int:
                return None
            if type(sender) != int:
                return sender
            return Message(message_type, sender)
        except:
            return None


class Process():
    def __init__(self, process_id: int, all_process_ids: List[int]):
        self.id = process_id
        self.all_process_ids = all_process_ids  # 全プロセスIDのリスト
        self.leader_id = None  # 現在のリーダーID リーダーが決まったら更新
        self.giveup = False

    def keep_listening(self):
        #ソケット通信でデータを受信する
        #データを受信したら別スレッドでhandle_messageを呼び出す
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", self.id))
        sock.listen(5)

        while True:
            client_sock, _ = sock.accept()
            client_sock.settimeout(0.5)
            t = threading.Thread(target=self.handle_message, args=(client_sock,))
            t.start()

    def ping(self) -> bool:
        # send 
        message = Message(PING, self.id)
        message_bytes = message.to_json_bytes()

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # Timeout: 0.5s
            sock.connect(("127.0.0.1", self.leader_id))
            sock.send(message_bytes)
            received = sock.recv(1024)
        except:
            return False

        received_message = Message.from_json_bytes(received)
        if received_message is None:
            return False
        if received_message.message_type != PONG:
            return False
        sock.close()
        return True
    
    def election_par_thread(self, dest_port: int):
        message_bytes = Message(ELECTION, self.id).to_json_bytes()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)

        try:
            sock.connect(("127.0.0.1", dest_port))
            print(f"connectted to {dest_port}")
            sock.send(message_bytes)
            data = sock.recv(1024)
            message = Message.from_json_bytes(data)
            if message is None:
                sock.close()
                return
            if message.message_type == OK:
                self.giveup = True
            sock.close()
        except Exception as e:
            print(e)
            return
    
    def send_message(self, dest_port: int, message: Message):
        message_data: bytes = message.to_json_bytes()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:            
            sock.settimeout(0.5)
            sock.connect(("127.0.0.1", dest_port))
            sock.send(message_data)
            sock.close()
        except Exception as e:
            print(e)
    
    def send_coordinator(self):
        coordinator_message = Message(COORDINATOR, self.id)
        for proc in self.all_process_ids:
            if proc == self.id:
                continue
            t = threading.Thread(target=self.send_message, args=(proc, coordinator_message))
            t.start()

    def election(self):
        print("選挙を開始")
        # TODO: OKが帰ってきたら、、、対応しないといけない。実装を見直す。
        threads = []
        for bigger_process in filter(lambda p: self.id < p, self.all_process_ids):
            t = threading.Thread(target=self.election_par_thread, args=(bigger_process,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        
        if self.giveup:
            self.giveup = False
            print("選挙負けた")
            return
        
        print("選挙勝った!")

        self.leader_id = self.id
        self.send_coordinator()


    def handle_message(self, sock: socket.socket):
        #keep_listeningから呼ばれ、受信したメッセージを処理する
        #メッセージタイプに応じて別の処理を行う
        try:
            data = sock.recv(1024)
            message = Message.from_json_bytes(data)
            if message is None:
                sock.close()
        except:
            return

        # メッセージタイプによって反応を切り替える
        if message.message_type == PING:
            self.reply_message(sock, PONG)
        if message.message_type == ELECTION:
            if message.sender <= self.id:
                self.reply_message(sock, OK)
            self.election()
        if message.message_type == COORDINATOR:
            print(f"New Leader: {message.sender}")
            self.leader_id = message.sender


    def run(self):
        print(f"[Process {self.id}] 起動しました。")
        #個別スレッドとしてソケット通信を待つkeep_listeningを起動
        listener_thread = threading.Thread(target=self.keep_listening)
        listener_thread.daemon = True
        listener_thread.start()

        # 初回の選挙
        self.election()

        while True:
            # 定期的にリーダーの存在を確認し、必要に応じて選挙を開始する
            # Ping to leader
            if self.leader_id != self.id and self.ping() == False:
                # TODO: leader election
                self.election()
            time.sleep(1)
    
    def reply_message(self, sock: socket.socket, message: int):
        message_bytes = Message(message, self.id).to_json_bytes()
        sock.send(message_bytes)
    

if __name__ == "__main__":
    # 簡単なテストのためにプロセスIDをいくつか定義
    process_ids = [10001, 10002, 10003]

    # ユーザーにどのプロセスを起動するか選ばせる
    #0なら10001、1なら10002、2なら10003を起動という具合
    index = input("Enter index (0, 1, or 2) to kill corresponding process after start: ")
    index = int(index) if index.isdigit() else None
    p = Process(process_ids[index], process_ids) 
    p.run()
