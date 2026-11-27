"""Shared pytest hooks.

SOV_TRADE_REQUIRE_FUNCTIONAL=1: any skipped test in an SC-SOV-TRADE-001
module (tests/test_sc_sov_trade_001*.py) is reported as a FAILURE, so a
missing dependency in CI cannot silently turn functional crypto, HSM,
timestamp, mTLS or ceremony tests into skips. xfail is unaffected (none
of these modules use it). Local development leaves the variable unset.
"""

from __future__ import annotations

import os

import pytest

_REQUIRE = os.environ.get("SOV_TRADE_REQUIRE_FUNCTIONAL", "") == "1"


def _is_sov_trade(path: str) -> bool:
    name = os.path.basename(path)
    return name.startswith("test_sc_sov_trade_001")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if not _REQUIRE or not report.skipped or hasattr(report, "wasxfail"):
        return
    if not _is_sov_trade(str(item.fspath)):
        return
    reason = report.longrepr[2] if isinstance(report.longrepr, tuple) else str(report.longrepr)
    report.outcome = "failed"
    report.longrepr = (
        "SOV_TRADE_REQUIRE_FUNCTIONAL=1: skipped functional test counts as a failure: "
        f"{reason}"
    )


def pytest_collectreport(report):
    # A module-level skip (pytest.skip(allow_module_level=True)) or an import
    # error in a sov_trade module must also fail under the flag.
    if _REQUIRE and report.skipped and _is_sov_trade(str(report.nodeid)):
        report.outcome = "failed"
