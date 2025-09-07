import threading
import socket
import json
import time

class Process():
    def __init__(self, process_id, all_process_ids):
        super().__init__()
        self.id = process_id
        self.all_process_ids = all_process_ids  # 全プロセスIDのリスト
        self.leader_id = None  # 現在のリーダーID リーダーが決まったら更新
        self.heard_from_leader = False
        self.received_ok = False

    def keep_listening(self):
        #ソケット通信でデータを受信する
        #データを受信したら別スレッドでhandle_messageを呼び出す
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('localhost', self.id))
        #プログラム終了時にソケットを解放する
        sock.listen()

        while True:
            conn, addr = sock.accept()
            with conn:
                data = conn.recv(1024)
                if data:
                    #json decode 
                    message = json.loads(data.decode('utf-8'))
                    threading.Thread(target=self.handle_message, args=(message,)).start()

    def send_message(self, target_port, message):
        #ソケット通信でデータを送信する
        #メッセージにメッセージタイプを付与することで受信側が handle_message() で識別できるようにする
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(('localhost', target_port))
            sock.sendall(json.dumps(message).encode('utf-8'))
        except ConnectionRefusedError:
            pass 
        finally:
            sock.close()

    def handle_message(self, message):
        #keep_listeningから呼ばれ、受信したメッセージを処理する
        #メッセージタイプに応じて別の処理を行う
        message_type = message.get("type")
        if message_type == "HEARTBEAT": 
            sender_id = message.get("from")
            self.send_message(sender_id, {"type": "ALIVE", "from": self.id})

        if message_type == "ALIVE":
            self.heard_from_leader = True
        
        if message_type == "ELECTION":
            sender_id = message.get("from")
            print(f"[Process {self.id}] プロセス {sender_id} から選挙メッセージを受信しました。")
            self.send_message(sender_id, {"type": "OK", "from": self.id})
            self.start_election()

        if message_type == "OK":
            self.received_ok = True
        if message_type == "COORDINATOR":
            new_leader_id = message.get("leader_id")
            self.leader_id = new_leader_id
            print(f"[Process {self.id}] 新しいリーダーはプロセス {self.leader_id} です。")
        
    def start_election(self):
        print(f"[Process {self.id}] 選挙を開始します。")
        higher_ids = [pid for pid in self.all_process_ids if pid > self.id]
        if not higher_ids:
            # 自分が最高IDなら即座にリーダーになる
            self.leader_id = self.id
            print(f"[Process {self.id}] 私が新しいリーダーです。")
            for pid in self.all_process_ids:
                if pid != self.id:
                    self.send_message(pid, {"type": "COORDINATOR", "leader_id": self.id})
        else:
            # 自分より高いIDのプロセスにELECTIONメッセージを送る
            for pid in higher_ids:
                self.send_message(pid, {"type": "ELECTION", "from": self.id})
            self.received_ok = False
            time.sleep(3) 
            if not self.received_ok:
                # 高いIDのプロセスからOKが来なかった場合、自分がリーダーになる
                self.leader_id = self.id
                print(f"[Process {self.id}] 私が新しいリーダーです。")
                for pid in self.all_process_ids:
                    if pid != self.id:
                        self.send_message(pid, {"type": "COORDINATOR", "leader_id": self.id})


    def run(self):
        print(f"[Process {self.id}] 起動しました。")
        #個別スレッドとしてソケット通信を待つkeep_listeningを起動
        listener_thread = threading.Thread(target=self.keep_listening)
        listener_thread.daemon = True
        listener_thread.start()

        while True:
            # 定期的にリーダーの存在を確認し、必要に応じて選挙を開始する
            self.send_message(self.leader_id, {"type": "HEARTBEAT", "from": self.id}) if self.leader_id else None
            
            time.sleep(2)
            if not self.heard_from_leader and not self.leader_id == self.id:
               print(f"[Process {self.id}] リーダーからの応答がありません。選挙を開始します。")
               self.start_election()
            else:
                self.heard_from_leader = False
        
           

           

if __name__ == "__main__":
    # 簡単なテストのためにプロセスIDをいくつか定義
    process_ids = [10001, 10002, 10003]

    # ユーザーにどのプロセスを起動するか選ばせる
    #0なら10001、1なら10002、2なら10003を起動という具合
    index = input("Enter index (0, 1, or 2) to kill corresponding process after start: ")
    index = int(index) if index.isdigit() else None
    p = Process(process_ids[index], process_ids) 
    p.run()