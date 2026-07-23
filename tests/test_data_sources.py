from collections import deque
import unittest

from reliability import DataManager, FetchResult


class SequenceSource:
    def __init__(self, values):
        self.values = deque(values)

    def __call__(self):
        value = self.values.popleft()
        if isinstance(value, Exception):
            raise value
        return value


class DataManagerTests(unittest.TestCase):
    def test_successful_refresh_is_healthy(self):
        manager = DataManager({"demo": lambda: {"value": 42}})

        snapshot = manager.refresh_once()["demo"]

        self.assertEqual(snapshot.status, "healthy")
        self.assertEqual(snapshot.data, {"value": 42})
        self.assertIsNotNone(snapshot.last_success_at)

    def test_warning_marks_source_as_degraded(self):
        manager = DataManager(
            {"demo": lambda: FetchResult({"value": 42}, warning="partial response")}
        )

        snapshot = manager.refresh_once()["demo"]

        self.assertEqual(snapshot.status, "degraded")
        self.assertEqual(snapshot.message, "partial response")

    def test_failed_refresh_keeps_last_known_good_data(self):
        source = SequenceSource([{"value": 42}, RuntimeError("source unavailable")])
        manager = DataManager({"demo": source})

        first = manager.refresh_once()["demo"]
        second = manager.refresh_once()["demo"]

        self.assertEqual(first.status, "healthy")
        self.assertEqual(second.status, "stale")
        self.assertEqual(second.data, {"value": 42})
        self.assertEqual(second.last_success_at, first.last_success_at)
        self.assertEqual(second.message, "source unavailable")

    def test_initial_failure_has_no_fake_fallback(self):
        def failing_source():
            raise RuntimeError("source unavailable")

        manager = DataManager({"demo": failing_source})

        snapshot = manager.refresh_once()["demo"]

        self.assertEqual(snapshot.status, "error")
        self.assertIsNone(snapshot.data)

    def test_health_history_is_bounded(self):
        manager = DataManager(
            {"demo": lambda: {"value": 42}},
            history_limit=2,
        )

        for _ in range(3):
            manager.refresh_once()

        self.assertEqual(len(manager.get_health_history()["demo"]), 2)


if __name__ == "__main__":
    unittest.main()
