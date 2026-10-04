"""
Feature: Run test cases with per-test timeouts and structured result reporting.

Usage:
    runner = TimeoutTestRunner(timeout_seconds=5.0, retries=1)
    results = runner.run_all([
        TestCase(name="test_addition", func=lambda: add(1, 2) == 3),
        TestCase(name="test_slow",    func=slow_operation),
    ])
    print(runner.summary(results))
    runner.export_json(results, "results.json")
"""

from __future__ import annotations

import json
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import dataclass, field, asdict
from typing import Callable, Iterable, Any, Optional


@dataclass
class TestCase:
    name: str
    func: Callable[[], Any]
    # A test "passes" if func returns True, or returns None without raising.
    expected: Optional[Any] = None


@dataclass
class TestResult:
    name: str
    passed: bool
    duration: float
    attempts: int = 1
    error: Optional[str] = None
    skipped: bool = False


@dataclass
class TimeoutTestRunner:
    timeout_seconds: float = 5.0
    retries: int = 0
    max_workers: int = 4
    _executor: ThreadPoolExecutor = field(init=False, repr=False)

    def __post_init__(self):
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers)

    # ---------- single test ----------
    def _run_once(self, case: TestCase) -> TestResult:
        start = time.perf_counter()
        future = self._executor.submit(case.func)
        try:
            value = future.result(timeout=self.timeout_seconds)
            duration = time.perf_counter() - start
            if case.expected is not None:
                passed = value == case.expected
                error = None if passed else f"expected {case.expected!r}, got {value!r}"
            else:
                passed = value is not False  # None or True => pass
                error = None
            return TestResult(case.name, passed, duration, error=error)
        except FuturesTimeout:
            return TestResult(
                case.name, False,
                time.perf_counter() - start,
                error=f"Timeout after {self.timeout_seconds}s",
            )
        except Exception:
            return TestResult(
                case.name, False,
                time.perf_counter() - start,
                error=traceback.format_exc(),
            )

    # ---------- with retries ----------
    def run(self, case: TestCase) -> TestResult:
        result = self._run_once(case)
        attempts = 1
        while not result.passed and attempts <= self.retries:
            attempts += 1
            result = self._run_once(case)
            result.attempts = attempts
        return result

    # ---------- batch ----------
    def run_all(self, cases: Iterable[TestCase]) -> list[TestResult]:
        return [self.run(c) for c in cases]

    # ---------- reporting ----------
    def summary(self, results: list[TestResult]) -> str:
        total = len(results)
        passed = sum(r.passed for r in results)
        lines = [f"Ran {total} tests: {passed} passed, {total - passed} failed"]
        for r in results:
            mark = "PASS" if r.passed else "FAIL"
            extra = f" ({r.attempts} attempts)" if r.attempts > 1 else ""
            lines.append(f"  [{mark}] {r.name} - {r.duration:.3f}s{extra}")
            if not r.passed and r.error:
                lines.append(f"        -> {r.error.strip().splitlines()[-1]}")
        return "\n".join(lines)

    def export_json(self, results: list[TestResult], path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in results], f, indent=2)

    def shutdown(self):
        self._executor.shutdown(wait=False, cancel_futures=True)


# ---------- demo ----------
if __name__ == "__main__":
    def ok():            return True
    def slow():          time.sleep(10); return True
    def flaky():
        # Fails ~50% of the time; with retries=1 it usually passes.
        import random
        return random.random() > 0.5

    runner = TimeoutTestRunner(timeout_seconds=1.0, retries=1)
    cases = [
        TestCase("test_ok", ok),
        TestCase("test_slow", slow),
        TestCase("test_flaky", flaky),
    ]
    results = runner.run_all(cases)
    print(runner.summary(results))
    runner.export_json(results, "results.json")
    runner.shutdown()
