#!/usr/bin/env python3
"""Generate daily test metrics markdown from coverage and report artifacts."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Iterable


FAILED_STATUSES = {"failed", "timedout", "timed_out", "interrupted", "unexpected", "error"}


def read_json_file(path: Path) -> Any:
    """Read JSON from path and return parsed content."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def as_float(value: Any) -> float | None:
    """Try to convert a value to float; return None when conversion is not possible."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def extract_coverage_percent(coverage_data: Any) -> float:
    """Extract API coverage percent from common coverage JSON shapes."""
    if not isinstance(coverage_data, dict):
        return 0.0

    totals = coverage_data.get("totals")
    if isinstance(totals, dict):
        for key in ("percent_covered", "percent_statements_covered", "percent_covered_display"):
            percent = as_float(totals.get(key))
            if percent is not None:
                return percent

    for key in ("coverage", "coverage_percent", "percent_covered", "percent"):
        percent = as_float(coverage_data.get(key))
        if percent is not None:
            return percent

    return 0.0


def build_test_name(parts: Iterable[str]) -> str:
    """Join non-empty title fragments into a stable test name."""
    cleaned = [part.strip() for part in parts if part and part.strip()]
    return " > ".join(cleaned) if cleaned else "Unknown test"


def test_status_from_record(test_record: dict[str, Any]) -> str:
    """Resolve the final status for a Playwright test record."""
    status = str(test_record.get("status", "")).strip().lower()
    if status:
        return status

    results = test_record.get("results")
    if isinstance(results, list) and results:
        latest = results[-1]
        if isinstance(latest, dict):
            return str(latest.get("status", "")).strip().lower()

    return ""


def parse_playwright_results(results_path: Path) -> tuple[int, int, Counter[str]]:
    """Count passed/failed tests and collect failures by test name from Playwright JSON."""
    if not results_path.exists():
        return 0, 0, Counter()

    data = read_json_file(results_path)
    passed = 0
    failed = 0
    failures: Counter[str] = Counter()

    def walk_suites(suites: Any, parent_titles: list[str]) -> None:
        nonlocal passed, failed
        if not isinstance(suites, list):
            return

        for suite in suites:
            if not isinstance(suite, dict):
                continue

            suite_title = str(suite.get("title", "")).strip()
            current_titles = parent_titles + ([suite_title] if suite_title else [])

            specs = suite.get("specs")
            if isinstance(specs, list):
                for spec in specs:
                    if not isinstance(spec, dict):
                        continue
                    spec_title = str(spec.get("title", "")).strip()
                    tests = spec.get("tests")
                    if not isinstance(tests, list):
                        continue
                    for test in tests:
                        if not isinstance(test, dict):
                            continue
                        status = test_status_from_record(test)
                        test_title = str(test.get("title", "")).strip()
                        name = build_test_name(
                            current_titles
                            + [spec_title]
                            + ([test_title] if test_title and test_title != spec_title else [])
                        )
                        if status == "passed" or status == "flaky":
                            passed += 1
                        elif status in FAILED_STATUSES:
                            failed += 1
                            failures[name] += 1

            walk_suites(suite.get("suites"), current_titles)

    walk_suites(data.get("suites"), [])

    if passed == 0 and failed == 0 and isinstance(data, dict):
        stats = data.get("stats")
        if isinstance(stats, dict):
            expected = int(stats.get("expected", 0) or 0)
            unexpected = int(stats.get("unexpected", 0) or 0)
            passed += expected
            failed += unexpected

    return passed, failed, failures


def parse_html_report_filenames(reports_dir: Path) -> tuple[int, int, Counter[str]]:
    """Count pass/fail signals from report HTML filenames."""
    passed = 0
    failed = 0
    failures: Counter[str] = Counter()
    pass_pattern = re.compile(r"pass(?:ed)?", re.IGNORECASE)
    fail_pattern = re.compile(r"fail(?:ed|ure|ures)?", re.IGNORECASE)

    for html_file in reports_dir.glob("*.html"):
        stem = html_file.stem.replace("_", " ").replace("-", " ").strip() or html_file.name
        if fail_pattern.search(html_file.name):
            failed += 1
            failures[stem] += 1
        elif pass_pattern.search(html_file.name):
            passed += 1

    return passed, failed, failures


def extract_previous_pass_rate(metrics_path: Path) -> float | None:
    """Extract pass rate from an existing metrics markdown file."""
    text = metrics_path.read_text(encoding="utf-8")
    patterns = (
        r"Overall test pass rate:\s*\*\*(\d+(?:\.\d+)?)%",
        r"\((\d+(?:\.\d+)?)% pass rate\)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def trend_indicator(reports_dir: Path, target_path: Path, current_rate: float) -> str:
    """Return UP/DOWN/STABLE trend versus latest previous metrics report."""
    metrics_files = sorted(reports_dir.glob("metrics-*.md"))
    previous_files = [path for path in metrics_files if path != target_path]
    if not previous_files:
        return "STABLE"

    previous_rate = extract_previous_pass_rate(previous_files[-1])
    if previous_rate is None:
        return "STABLE"
    if current_rate > previous_rate:
        return "UP"
    if current_rate < previous_rate:
        return "DOWN"
    return "STABLE"


def format_top_failures(failures: Counter[str]) -> str:
    """Create markdown for top-3 failing tests."""
    top_three = failures.most_common(3)
    if not top_three:
        return "- None"
    lines = [f"- {name} ({count})" for name, count in top_three]
    return "\n".join(lines)


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    reports_dir = repo_root / "reports"
    coverage_path = reports_dir / "coverage.json"
    playwright_path = repo_root / "web-app" / "playwright-report" / "results.json"

    if not coverage_path.exists():
        print(f"Missing required coverage file: {coverage_path}", file=sys.stderr)
        return 1

    reports_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    output_path = reports_dir / f"metrics-{today}.md"

    coverage_data = read_json_file(coverage_path)
    coverage_percent = extract_coverage_percent(coverage_data)

    playwright_passed, playwright_failed, playwright_failures = parse_playwright_results(playwright_path)
    html_passed, html_failed, html_failures = parse_html_report_filenames(reports_dir)

    web_passed = playwright_passed + html_passed
    web_failed = playwright_failed + html_failed
    total_tests = web_passed + web_failed
    pass_rate = (web_passed / total_tests * 100.0) if total_tests else 0.0

    combined_failures = playwright_failures + html_failures
    trend = trend_indicator(reports_dir, output_path, pass_rate)

    markdown = (
        f"# Test Metrics ({today})\n\n"
        f"- Overall test pass rate: **{pass_rate:.1f}%**\n"
        f"- API test coverage: **{coverage_percent:.1f}%**\n"
        f"- Web tests: **{web_passed} passed / {web_failed} failed**\n"
        f"- Trend: **{trend}**\n\n"
        "## Top 3 most-failing tests\n"
        f"{format_top_failures(combined_failures)}\n"
    )

    output_path.write_text(markdown, encoding="utf-8")

    print(
        f"Tests: {web_passed} passed, {web_failed} failed ({pass_rate:.1f}% pass rate) | "
        f"Coverage: {coverage_percent:.1f}%"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
