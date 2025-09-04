from .process import Process
import multiprocessing

class Cluster:
    def __init__(self, num_processes):
        self.processes = [Process(i) for i in range(num_processes)]

    def start_all(self):
        for process in self.processes:
            self.start_process(process.id)

    def kill_process(self, id):
        for process in self.processes:
            if process.id == id:
                process.kill()
                break
    
    def start_process(self, id):
        process = multiprocessing.Process(target=self.processes[id].run)
        process.start()
