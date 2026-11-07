import random
import unittest
from dynamic_rag.simulator import POLICIES, make_episodes, run_episode

class SimulatorTests(unittest.TestCase):
    def test_episode_generation_is_deterministic(self):
        self.assertEqual(make_episodes(5, 17), make_episodes(5, 17))

    def test_all_policies_return_valid_metrics(self):
        ep = make_episodes(1, 23)[0]
        for policy in POLICIES:
            row, trace = run_episode(ep, policy, random.Random(99))
            self.assertEqual(len(trace), ep.steps)
            self.assertGreaterEqual(row["wrong_steps"], 0)
            self.assertLessEqual(row["wrong_steps"], ep.steps)
            self.assertIn(row["episode_success"], (0, 1))

    def test_unknown_policy_fails(self):
        ep = make_episodes(1, 1)[0]
        with self.assertRaises(ValueError):
            run_episode(ep, "not-a-policy", random.Random(1))

if __name__ == "__main__":
    unittest.main()
