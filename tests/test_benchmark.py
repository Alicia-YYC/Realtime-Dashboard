import unittest

from benchmark import measure, summarize
from reliability import DataManager


class BenchmarkTests(unittest.TestCase):
    def test_failed_pairs_cannot_inflate_speedup(self):
        def cycle(seconds, healthy):
            return {"elapsed_seconds": seconds, "all_healthy": healthy,
                    "sources": {"source": {"status": "healthy" if healthy else "error"}}}
        result = summarize([
            {"sequential": cycle(4, True), "concurrent": cycle(2, True)},
            {"sequential": cycle(4, True), "concurrent": cycle(0.001, False)},
        ])
        self.assertEqual(result["eligible_pairs"], 1)
        self.assertEqual(result["excluded_pairs"], 1)
        self.assertEqual(result["median_refresh_reduction_percent"], 50)

    def test_no_healthy_pairs_has_no_performance_claim(self):
        failed = {"all_healthy": False, "elapsed_seconds": 0.01,
                  "sources": {"source": {"status": "error"}}}
        result = summarize([{"sequential": failed, "concurrent": failed}])
        self.assertEqual(result["eligible_pairs"], 0)
        self.assertIsNone(result["median_refresh_reduction_percent"])

    def test_both_execution_modes_preserve_successful_sources_during_failure(self):
        def fail():
            raise RuntimeError("unavailable")
        for concurrent in (False, True):
            with self.subTest(concurrent=concurrent):
                manager = DataManager({"good": lambda: {"value": 42}, "bad": fail})
                result = measure(manager, concurrent=concurrent)
                self.assertFalse(result["all_healthy"])
                self.assertEqual(result["sources"]["good"]["status"], "healthy")
                self.assertEqual(result["sources"]["bad"]["status"], "error")
                self.assertEqual(manager.get_snapshots()["good"].data, {"value": 42})


if __name__ == "__main__":
    unittest.main()
