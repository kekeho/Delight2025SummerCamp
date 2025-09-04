class Process:
    process_list = []
    
    
    def __init__(self, id):
        self.id = id


    def run(self):
        while True:
            print(f"Process {self.id} is running.")