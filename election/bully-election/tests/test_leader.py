import time
import unittest
from src.cluster import Cluster

class TestBullyElection(unittest.TestCase):
    def test_leader_exists_after_start(self):
        cluster = Cluster(10)
        cluster.start_all()
        time.sleep(2)
        # リーダーが存在するか確認
        leaders = [p.id for p in cluster.processes.values() if p.is_leader]
        print("Leaders:", leaders)
        cluster.check_leader()
        #self.assertEqual(len(leaders), 1)
        # テスト終了後に全プロセスをkill
        print("Killing all processes")
        cluster.kill_all()

        
    def test_leader_election_after_kill(self):
        cluster = Cluster(10)
        cluster.start_all()
        time.sleep(2)
        # 最初のリーダーを確認
        initial_leaders = [p.id for p in cluster.processes.values() if p.is_leader]
        print("Initial Leaders:", initial_leaders)
        self.assertEqual(len(initial_leaders), 1)
        
        # リーダーをkill
        if initial_leaders:
            cluster.kill_process(initial_leaders[0])
            time.sleep(5)
        # 新しいリーダーが選出されたか確認
        cluster.check_leader()
        # テスト終了後に全プロセスをkill
        print("Killing all processes")
        cluster.kill_all()


if __name__ == "__main__":
    unittest.main()
