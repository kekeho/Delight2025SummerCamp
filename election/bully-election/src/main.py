from .cluster import Cluster
import time

if __name__ == "__main__":
    cluster = Cluster()
    cluster.start_all()
    
    time.sleep(2)
    print("Killing process 2")
    cluster.kill_process(2)
    
    
    time.sleep(5)  # Let the processes run for a while before exiting
    cluster.check_leader()