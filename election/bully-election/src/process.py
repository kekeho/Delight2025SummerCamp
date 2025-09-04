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
        pass
