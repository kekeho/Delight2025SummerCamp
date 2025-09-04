import multiprocessing
import time

class Process(multiprocessing.Process):
    def __init__(self, process_id):
        super().__init__()
        self.id = process_id
        self.is_leader = False
        self.leader_id = None
        self.process_list = []
    
    

    def run(self):
        print(f"[Process {self.id}] 起動しました。")
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            pass 
        finally:
            print(f"[Process {self.id}] 終了します。")