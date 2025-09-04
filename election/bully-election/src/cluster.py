from .process import Process

class Cluster:
    def __init__(self):
        # bully.confからポート番号一覧を取得
        with open("src/bully.conf", "r") as f:
            self.process_ports= [int(line.strip().split(":")[1]) for line in f if line.strip()]
        # クラスターIDをポート番号に一致させてProcessを生成
        self.processes = {i: Process(i) for i in range(len(self.process_ports))}
        # 各Processにポート番号一覧を渡す
        for i, process in self.processes.items():
            process.process_list = self.process_ports
            process.id = self.process_ports[i]
        print(f"{len(self.process_ports)}個のプロセスを準備しました。")
        

            

    def start_all(self):
        print("--- 全てのプロセスを起動します ---")
        for process in self.processes.values():
            process.start() 

    def kill_process(self, process_id):
        process = self.processes.get(process_id)
        if process and process.is_alive():
            print(f"--- プロセス {process_id} を強制終了します ---")
            process.kill() 
        elif process:
            print(f"プロセス {process_id} は既に終了しています。")
        else:
            print(f"プロセスID {process_id} は存在しません。")
            
    def join_all(self):
        print("--- 全てのプロセスの終了を待機します ---")
        for process in self.processes.values():
            process.join()
    
    def check_leader(self):
        leaders = [p.id for p in self.processes.values() if p.is_leader]
        if len(leaders) == 1:
            max_alive = max(p.id for p in self.processes.values() if p.is_alive())
            if leaders[0] == max_alive:
                print(f"現在のリーダーはプロセス {leaders[0]} です。")
            else:
                print(f"エラー: リーダー {leaders[0]} は最大IDの稼働中プロセスではありません。")

        elif len(leaders) > 1:
            print(f"エラー: 複数のリーダーが存在します: {leaders}")
        else:
            print("現在リーダーは存在しません。")