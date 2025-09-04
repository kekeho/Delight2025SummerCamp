from .process import Process

class Cluster:
    def __init__(self, num_processes):
        self.processes = {i: Process(i) for i in range(num_processes)}
        print(f"{num_processes}個のプロセスを準備しました。")

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