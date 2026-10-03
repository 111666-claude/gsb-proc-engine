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
        self.assertEqual(engine.triggers("p1"), 0)

    def test_reregister_moves_subscription(self):
        engine = Engine()
        engine.register("p1", "hit")
        engine.register("p1", "kill")
        self.assertEqual(engine.fire("hit", 0, "e1"), [])
        self.assertEqual(engine.fire("kill", 0, "e2"), ["p1"])


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

    def test_zero_icd_always_fires(self):
        engine = Engine()
        engine.register("p1", "hit")
        engine.fire("hit", 0, "e1")
        self.assertEqual(engine.fire("hit", 0, "e2"), ["p1"])


class CapTest(unittest.TestCase):
    def test_max_triggers_enforced(self):
        engine = Engine()
        engine.register("p1", "hit", max_triggers=2)
        for index in range(3):
            engine.fire("hit", index * 1000, "e-%d" % index)
        self.assertEqual(engine.triggers("p1"), 2)

    def test_zero_max_triggers_means_unlimited(self):
        engine = Engine()
        engine.register("p1", "hit")
        for index in range(5):
            engine.fire("hit", index, "e-%d" % index)
        self.assertEqual(engine.triggers("p1"), 5)


class IdempotencyTest(unittest.TestCase):
    def test_same_event_id_processed_once(self):
        engine = Engine()
        engine.register("p1", "hit")
        self.assertEqual(engine.fire("hit", 0, "same"), ["p1"])
        self.assertEqual(engine.fire("hit", 0, "same"), [])
        self.assertEqual(engine.triggers("p1"), 1)

    def test_duplicate_dispatch_does_not_scan(self):
        engine = Engine()
        engine.register("p1", "hit")
        engine.fire("hit", 0, "same")
        scanned = engine.scanned_count()
        engine.fire("hit", 0, "same")
        self.assertEqual(engine.scanned_count(), scanned)


class InvariantTest(unittest.TestCase):
    def test_proc_appears_at_most_once_per_dispatch(self):
        engine = Engine()
        engine.register("p1", "hit")
        engine.register("p2", "hit")
        fired = engine.fire("hit", 0, "e1")
        self.assertEqual(len(fired), len(set(fired)))

    def test_triggers_never_decrease(self):
        engine = Engine()
        engine.register("p1", "hit", icd_ms=1000, max_triggers=2)
        last = 0
        for index in range(5):
            engine.fire("hit", index * 500, "e-%d" % index)
            current = engine.triggers("p1")
            self.assertGreaterEqual(current, last)
            last = current

    def test_repeated_sequence_same_result(self):
        def run():
            engine = Engine()
            engine.register("p1", "hit", icd_ms=100)
            engine.register("p2", "kill", max_triggers=1)
            return [engine.fire("hit", t, "e-%d" % t) for t in (0, 50, 150)]
        self.assertEqual(run(), run())

    def test_scanned_not_linear_in_registrations(self):
        engine = Engine()
        for index in range(3000):
            engine.register("p-%d" % index, "hit")
        for index in range(3000):
            engine.fire("kill", index, "e-%d" % index)
        self.assertLessEqual(engine.scanned_count(), 6000)
