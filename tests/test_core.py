import unittest

from procs.core import Engine


class BasicTest(unittest.TestCase):
    def test_empty_engine_fires_nothing(self):
        self.assertEqual(Engine().fire("hit", 0, "e1"), [])

    def test_register_then_triggers_zero(self):
        engine = Engine()
        engine.register("p1", "hit")
        self.assertEqual(engine.triggers("p1"), 0)

    def test_unknown_proc_triggers_zero(self):
        self.assertEqual(Engine().triggers("ghost"), 0)

    def test_register_overwrites(self):
        engine = Engine()
        engine.register("p1", "hit")
        engine.register("p1", "kill")
        self.assertEqual(engine.procs["p1"]["event"], "kill")

    def test_scanned_starts_at_zero(self):
        self.assertEqual(Engine().scanned_count(), 0)


if __name__ == "__main__":
    unittest.main()
