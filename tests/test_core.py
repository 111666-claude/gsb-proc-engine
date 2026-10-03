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


class EventFilterTest(unittest.TestCase):
    def test_only_subscribed_procs_fire(self):
        engine = Engine()
        engine.register("p1", "hit")
        engine.register("p2", "kill")
        self.assertEqual(engine.fire("hit", 0, "e1"), ["p1"])
        self.assertEqual(engine.triggers("p2"), 0)

    def test_unsubscribed_event_fires_nothing(self):
        engine = Engine()
        engine.register("p1", "hit")
        self.assertEqual(engine.fire("kill", 0, "e1"), [])

    def test_scanned_counts_only_subscribers(self):
        engine = Engine()
        for index in range(100):
            engine.register("p-%d" % index, "hit")
        engine.fire("kill", 0, "e1")
        self.assertEqual(engine.scanned_count(), 0)
        engine.fire("hit", 0, "e2")
        self.assertEqual(engine.scanned_count(), 100)


class IcdTest(unittest.TestCase):
    def test_within_icd_does_not_fire(self):
        engine = Engine()
        engine.register("p1", "hit", icd_ms=1000)
        engine.fire("hit", 0, "e1")
        self.assertEqual(engine.fire("hit", 500, "e2"), [])
        self.assertEqual(engine.triggers("p1"), 1)

    def test_exactly_icd_fires(self):
        engine = Engine()
        engine.register("p1", "hit", icd_ms=1000)
        engine.fire("hit", 0, "e1")
        self.assertEqual(engine.fire("hit", 1000, "e2"), ["p1"])
        self.assertEqual(engine.triggers("p1"), 2)

    def test_icd_is_per_proc(self):
        engine = Engine()
        engine.register("p1", "hit", icd_ms=1000)
        engine.register("p2", "hit")
        engine.fire("hit", 0, "e1")
        self.assertEqual(engine.fire("hit", 500, "e2"), ["p2"])


class MaxTriggersTest(unittest.TestCase):
    def test_cap_stops_firing(self):
        engine = Engine()
        engine.register("p1", "hit", max_triggers=2)
        for index in range(3):
            engine.fire("hit", index * 1000, "e-%d" % index)
        self.assertEqual(engine.triggers("p1"), 2)

    def test_zero_means_unlimited(self):
        engine = Engine()
        engine.register("p1", "hit", max_triggers=0)
        for index in range(5):
            engine.fire("hit", index, "e-%d" % index)
        self.assertEqual(engine.triggers("p1"), 5)


class IdempotencyTest(unittest.TestCase):
    def test_duplicate_event_id_returns_empty(self):
        engine = Engine()
        engine.register("p1", "hit")
        self.assertEqual(engine.fire("hit", 0, "same"), ["p1"])
        self.assertEqual(engine.fire("hit", 0, "same"), [])
        self.assertEqual(engine.triggers("p1"), 1)

    def test_same_id_different_event_still_deduped(self):
        engine = Engine()
        engine.register("p1", "hit")
        engine.register("p2", "kill")
        engine.fire("hit", 0, "same")
        self.assertEqual(engine.fire("kill", 0, "same"), [])

    def test_replay_sequence_is_deterministic(self):
        def run():
            engine = Engine()
            engine.register("p1", "hit", icd_ms=100)
            engine.register("p2", "hit", max_triggers=1)
            engine.register("p3", "kill")
            return [engine.fire("hit", 0, "e1"),
                    engine.fire("hit", 50, "e2"),
                    engine.fire("hit", 100, "e3"),
                    engine.fire("hit", 100, "e3")]

        self.assertEqual(run(), run())
        self.assertEqual(run(), [["p1", "p2"], [], ["p1"], []])


if __name__ == "__main__":
    unittest.main()
