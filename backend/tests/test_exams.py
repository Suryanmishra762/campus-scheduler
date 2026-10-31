"""
Comprehensive tests for the Exam Scheduling System.

Covers:
  1.  All 41 exams scheduled
  2.  Valid exam-week slots only (Mon–Sat, AM/PM)
  3.  Half seating capacity enforced
  4.  Multi-room allocation (total seats ≥ exam size)
  5.  No student-group clash (same group, same slot)
  6.  No room double-booking (same room, same slot)
  7.  Room exam eligibility (allowed_uses includes "exam")
  8.  Room unavailability respected
  9.  Result structure and counts
  10. API routes registered
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.dataset import load_dataset
from app.examinations.engine import schedule_exams


# ── Fixtures ────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def result():
    return schedule_exams()


@pytest.fixture(scope="module")
def dataset():
    return load_dataset()


@pytest.fixture(scope="module")
def scheduled(result):
    return result["scheduled"]


@pytest.fixture(scope="module")
def exam_rooms(dataset):
    return {
        r["id"]: r
        for r in dataset["rooms"]
        if "exam" in r.get("allowed_uses", [])
    }


# ── 1. All 41 exams scheduled ──────────────────────────────────


class TestAllExamsScheduled:
    def test_total_exam_count(self, dataset):
        assert len(dataset["exams"]) == 41

    def test_all_exams_placed(self, result):
        assert result["scheduled_count"] == 41
        assert result["unscheduled_count"] == 0

    def test_no_unscheduled(self, result):
        assert result["unscheduled"] == []

    def test_scheduled_ids_match_dataset(self, result, dataset):
        scheduled_ids = {s["exam_id"] for s in result["scheduled"]}
        dataset_ids = {e["id"] for e in dataset["exams"]}
        assert scheduled_ids == dataset_ids


# ── 2. Valid exam-week slots ────────────────────────────────────


class TestValidSlots:
    def test_days_within_exam_week(self, scheduled, dataset):
        valid_days = set(dataset["calendar"]["exam_week"]["days"])
        for s in scheduled:
            assert s["day"] in valid_days, (
                f"{s['exam_id']} on invalid day {s['day']}"
            )

    def test_sessions_are_am_or_pm(self, scheduled):
        for s in scheduled:
            assert s["session"] in ("AM", "PM"), (
                f"{s['exam_id']} has invalid session {s['session']}"
            )


# ── 3. Half seating capacity ───────────────────────────────────


class TestHalfCapacity:
    def test_seats_used_within_half_capacity(self, scheduled, exam_rooms):
        for s in scheduled:
            for alloc in s["rooms"]:
                rid = alloc["room_id"]
                room = exam_rooms[rid]
                half_cap = room["capacity"] // 2
                assert alloc["seats_used"] <= half_cap, (
                    f"{s['exam_id']}: room {rid} uses {alloc['seats_used']} "
                    f"seats but half capacity is {half_cap}"
                )


# ── 4. Multi-room allocation covers exam size ──────────────────


class TestMultiRoomAllocation:
    def test_total_seats_cover_exam_size(self, scheduled):
        for s in scheduled:
            total_seats = sum(a["seats_used"] for a in s["rooms"])
            assert total_seats >= s["size"], (
                f"{s['exam_id']}: total seats {total_seats} "
                f"< exam size {s['size']}"
            )

    def test_large_exams_use_multiple_rooms(self, scheduled, exam_rooms):
        """Exams larger than the biggest half-capacity must split."""
        max_half = max(r["capacity"] // 2 for r in exam_rooms.values())
        for s in scheduled:
            if s["size"] > max_half:
                assert len(s["rooms"]) > 1, (
                    f"{s['exam_id']} (size {s['size']}) should use "
                    f"multiple rooms (max half-cap is {max_half})"
                )


# ── 5. No student-group clash ──────────────────────────────────


class TestGroupClashes:
    def test_no_group_overlap(self, scheduled):
        group_slots: dict[tuple[str, str, str], list[str]] = defaultdict(list)
        for s in scheduled:
            for gid in s["groups"]:
                key = (gid, s["day"], s["session"])
                group_slots[key].append(s["exam_id"])

        clashes = {k: v for k, v in group_slots.items() if len(v) > 1}
        assert len(clashes) == 0, f"Group clashes: {clashes}"


# ── 6. No room double-booking ──────────────────────────────────


class TestRoomClashes:
    def test_no_room_overlap(self, scheduled):
        room_slots: dict[tuple[str, str, str], list[str]] = defaultdict(list)
        for s in scheduled:
            for alloc in s["rooms"]:
                key = (alloc["room_id"], s["day"], s["session"])
                room_slots[key].append(s["exam_id"])

        clashes = {k: v for k, v in room_slots.items() if len(v) > 1}
        assert len(clashes) == 0, f"Room clashes: {clashes}"


# ── 7. Room exam eligibility ───────────────────────────────────


class TestRoomEligibility:
    def test_all_rooms_allow_exams(self, scheduled, dataset):
        room_by_id = {r["id"]: r for r in dataset["rooms"]}
        for s in scheduled:
            for alloc in s["rooms"]:
                room = room_by_id[alloc["room_id"]]
                assert "exam" in room.get("allowed_uses", []), (
                    f"{s['exam_id']}: room {alloc['room_id']} does "
                    f"not allow exams"
                )


# ── 8. Room unavailability ─────────────────────────────────────


class TestRoomUnavailability:
    def test_unavailable_rooms_not_used(self, scheduled, dataset):
        """Rooms with full-day closures should not be used on those days."""
        calendar = dataset["calendar"]
        all_teaching = set(
            p["id"] for p in calendar["periods"] if p["teaching"]
        )
        full_day_closures: set[tuple[str, str]] = set()
        for ru in dataset["room_unavailability"]:
            if all_teaching <= set(ru["periods"]):
                full_day_closures.add((ru["room_id"], ru["day"]))

        violations = []
        for s in scheduled:
            for alloc in s["rooms"]:
                if (alloc["room_id"], s["day"]) in full_day_closures:
                    violations.append(
                        f"{s['exam_id']}: room {alloc['room_id']} "
                        f"unavailable on {s['day']}"
                    )
        assert len(violations) == 0, f"Unavailability violations: {violations}"


# ── 9. Result structure ────────────────────────────────────────


class TestResultStructure:
    def test_counts_consistent(self, result):
        assert result["total_exams"] == (
            result["scheduled_count"] + result["unscheduled_count"]
        )
        assert result["scheduled_count"] == len(result["scheduled"])
        assert result["unscheduled_count"] == len(result["unscheduled"])

    def test_slots_available(self, result):
        # 6 days * 2 sessions = 12
        assert result["slots_available"] == 12

    def test_slots_used_positive(self, result):
        assert result["slots_used"] > 0
        assert result["slots_used"] <= result["slots_available"]


# ── 10. Route registration ─────────────────────────────────────


class TestRouteRegistration:
    def test_exam_routes_registered(self):
        from app.main import app

        schema = app.openapi()
        paths = schema["paths"]
        assert "/api/exams/schedule" in paths

