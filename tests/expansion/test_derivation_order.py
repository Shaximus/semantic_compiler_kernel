"""Tests for expansion.derivation_order."""

from semantic_compiler.expansion.derivation_order import (
    attach_derivation_event,
    build_event_log,
    compute_before_exposure,
    make_event,
)


def test_before_exposure_flags():
    assert compute_before_exposure("2026-01-01T00:00:00+00:00", "2026-02-01T00:00:00+00:00") is True
    assert compute_before_exposure("2026-02-01T00:00:00+00:00", "2026-01-01T00:00:00+00:00") is False
    # equal timestamps are not "before"
    assert compute_before_exposure("2026-01-01T00:00:00+00:00", "2026-01-01T00:00:00+00:00") is False


def test_missing_or_bad_timestamps_are_none_not_guessed():
    assert compute_before_exposure(None, "2026-01-01T00:00:00+00:00") is None
    assert compute_before_exposure("2026-01-01T00:00:00+00:00", None) is None
    assert compute_before_exposure("not-a-date", "2026-01-01T00:00:00+00:00") is None
    assert compute_before_exposure("", "") is None


def test_z_suffix_and_naive_timestamps():
    assert compute_before_exposure("2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z") is True
    # naive timestamps are treated as UTC
    assert compute_before_exposure("2026-01-01 10:00:00", "2026-01-01T10:00:01+00:00") is True


def test_make_event_and_to_dict():
    event = make_event(
        "claim-7",
        derived_at="2026-01-01T00:00:00+00:00",
        exposed_to_parallel_at="2026-03-01T00:00:00+00:00",
        note="independent derivation",
    )
    d = event.to_dict()
    assert d["subject_id"] == "claim-7"
    assert d["derived_before_exposure"] is True
    assert d["note"] == "independent derivation"


def test_attach_derivation_event_appends_non_mutating():
    record = {"invariant_id": "INV-0000"}
    e1 = make_event("INV-0000", derived_at="2026-01-01T00:00:00+00:00",
                    exposed_to_parallel_at="2026-02-01T00:00:00+00:00")
    e2 = make_event("INV-0000", derived_at="2026-01-01T00:00:00+00:00")
    out = attach_derivation_event(record, e1)
    out = attach_derivation_event(out, e2)
    assert "derivation_event_log" not in record
    assert len(out["derivation_event_log"]) == 2
    assert out["derivation_event_log"][0]["derived_before_exposure"] is True
    assert out["derivation_event_log"][1]["derived_before_exposure"] is None


def test_build_event_log():
    log = build_event_log([
        {"subject_id": "a", "derived_at": "2026-01-01T00:00:00+00:00",
         "exposed_to_parallel_at": "2026-01-02T00:00:00+00:00"},
        {"subject_id": "b"},
    ])
    assert log[0]["derived_before_exposure"] is True
    assert log[1]["derived_before_exposure"] is None
