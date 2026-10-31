"""
Focused tests for the Venue Booking and Approval System.

Covers:
  1.  Cancelled-request rejection
  2.  Role-category cap enforcement
  3.  Room capacity validation
  4.  Room type / feature matching
  5.  Accessibility filtering
  6.  Invalid-period / time-window rejection
  7.  Self-approval prevention
  8.  Priority-based processing order
  9.  Every request receives a decision with a valid status
  10. Approved bookings carry allocations; rejected ones do not
  11. No double-booking across all decisions
  12. Alternative-room offering when preferred room unavailable
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.bookings.engine import (
    check_role_permission,
    find_candidate_rooms,
    process_all_bookings,
    validate_single_booking,
)
from app.core.dataset import load_dataset


# ── Fixtures (computed once per module) ─────────────────────────


@pytest.fixture(scope="module")
def decisions():
    return process_all_bookings()


@pytest.fixture(scope="module")
def decision_map(decisions):
    return {d["request_id"]: d for d in decisions}


@pytest.fixture(scope="module")
def dataset():
    return load_dataset()


# ── 1. Cancelled request ───────────────────────────────────────


class TestCancelledRequests:
    def test_cancelled_request_rejected(self, decision_map):
        """BR-04 was cancelled and must be rejected."""
        d = decision_map["BR-04"]
        assert d["status"] == "rejected"
        assert any("cancelled" in r.lower() for r in d["reasons"])

    def test_cancelled_request_not_allocated(self, decision_map):
        d = decision_map["BR-04"]
        assert d["allocated"] is None
        assert d["alternative"] is None


# ── 2. Role-category cap ───────────────────────────────────────


class TestRoleCategoryCap:
    def test_club_cannot_book_guest_lecture(self, decision_map):
        """BR-12: club requesting guest_lecture exceeds its cap."""
        d = decision_map["BR-12"]
        assert d["status"] == "rejected"
        assert any("maximum" in r.lower() or "cannot book" in r.lower()
                    for r in d["reasons"])

    def test_club_cannot_book_institute_event(self, decision_map):
        """BR-15: club requesting institute_event exceeds its cap."""
        d = decision_map["BR-15"]
        assert d["status"] == "rejected"

    def test_admin_can_book_institute_event(self, decision_map):
        """BR-01: admin booking institute_event is within cap."""
        d = decision_map["BR-01"]
        # Must not be rejected *for role reasons*
        assert d["status"] != "rejected" or not any(
            "cannot book" in r.lower() for r in d["reasons"]
        )

    def test_faculty_can_book_guest_lecture(self, decision_map):
        """BR-03: faculty booking guest_lecture is within cap."""
        d = decision_map["BR-03"]
        assert d["status"] != "rejected" or not any(
            "cannot book" in r.lower() for r in d["reasons"]
        )

    def test_permission_helper_comprehensive(self):
        po = [
            "exam", "regular_session", "institute_event",
            "guest_lecture", "department_event", "club_event",
        ]
        cap = {
            "admin": "institute_event",
            "faculty": "guest_lecture",
            "department_coordinator": "department_event",
            "club": "club_event",
        }

        # Within cap — should return None (no error)
        assert check_role_permission("admin", "institute_event", po, cap) is None
        assert check_role_permission("admin", "club_event", po, cap) is None
        assert check_role_permission("faculty", "guest_lecture", po, cap) is None
        assert check_role_permission("faculty", "department_event", po, cap) is None
        assert check_role_permission("club", "club_event", po, cap) is None
        assert check_role_permission(
            "department_coordinator", "department_event", po, cap,
        ) is None

        # Exceeds cap — should return an error string
        assert check_role_permission("club", "guest_lecture", po, cap) is not None
        assert check_role_permission("club", "institute_event", po, cap) is not None
        assert check_role_permission("faculty", "institute_event", po, cap) is not None
        assert check_role_permission(
            "department_coordinator", "guest_lecture", po, cap,
        ) is not None


# ── 3. Room capacity ───────────────────────────────────────────


class TestRoomCapacity:
    def test_oversized_event_rejected(self, decision_map):
        """BR-09: attendance 1200 exceeds every compatible room."""
        d = decision_map["BR-09"]
        assert d["status"] == "rejected"
        assert any(
            "no room" in r.lower() or "capacity" in r.lower()
            for r in d["reasons"]
        )


# ── 4. Time-window validation ──────────────────────────────────


class TestTimeWindows:
    def test_invalid_period_rejected(self, decision_map):
        """BR-17: window references period 14 (does not exist)."""
        d = decision_map["BR-17"]
        assert d["status"] == "rejected"
        assert any(
            "time slot" in r.lower() or "no available" in r.lower()
            for r in d["reasons"]
        )


# ── 5. Self-approval ───────────────────────────────────────────


class TestSelfApproval:
    def test_self_approval_rejected(self):
        req = {
            "id": "TEST-SELF",
            "title": "Test event",
            "requester": "Alice",
            "role": "admin",
            "requested_category": "institute_event",
            "attendance": 50,
            "duration_periods": 1,
            "windows": [{"day": "MON", "from_period": 10, "to_period": 10}],
            "room_types": ["seminar_hall"],
            "needs": [],
        }
        d = validate_single_booking(req, approver="Alice")
        assert d["status"] == "rejected"
        assert any("self-approval" in r.lower() for r in d["reasons"])

    def test_different_approver_allowed(self):
        req = {
            "id": "TEST-OTHER",
            "title": "Test event",
            "requester": "Alice",
            "role": "admin",
            "requested_category": "institute_event",
            "attendance": 50,
            "duration_periods": 1,
            "windows": [{"day": "MON", "from_period": 10, "to_period": 10}],
            "room_types": ["seminar_hall"],
            "needs": [],
        }
        d = validate_single_booking(req, approver="Bob")
        # Should not be rejected for self-approval
        assert d["status"] != "rejected" or not any(
            "self-approval" in r.lower() for r in d["reasons"]
        )


# ── 6. Completeness & valid statuses ───────────────────────────


class TestCompleteness:
    def test_all_requests_have_decisions(self, decisions, dataset):
        """Every booking request in the dataset must receive a decision."""
        request_ids = {br["id"] for br in dataset["booking_requests"]}
        decision_ids = {d["request_id"] for d in decisions}
        assert request_ids == decision_ids

    def test_valid_statuses_only(self, decisions):
        valid = {"approved", "rejected", "alternative_offered"}
        for d in decisions:
            assert d["status"] in valid, (
                f"{d['request_id']} has invalid status: {d['status']}"
            )

    def test_no_empty_reasons(self, decisions):
        for d in decisions:
            assert len(d["reasons"]) > 0, (
                f"{d['request_id']} has no reasons"
            )


# ── 7. Priority ordering ───────────────────────────────────────


class TestPriorityOrdering:
    def test_decisions_ordered_by_priority_then_time(self, decisions):
        """Decision list follows (priority_index, submitted_at) order."""
        ds = load_dataset()
        po = ds["priority_order"]
        br_map = {br["id"]: br for br in ds["booking_requests"]}

        prev_key: tuple[int, str] = (-1, "")
        for d in decisions:
            br = br_map.get(d["request_id"])
            if not br:
                continue
            cat = br["requested_category"]
            idx = po.index(cat) if cat in po else len(po)
            cur_key = (idx, br["submitted_at"])
            assert cur_key >= prev_key, (
                f"Order violation at {d['request_id']}: "
                f"{cur_key} should not precede {prev_key}"
            )
            prev_key = cur_key


# ── 8. Allocation integrity ────────────────────────────────────


class TestAllocationIntegrity:
    def test_approved_has_allocation(self, decisions):
        for d in decisions:
            if d["status"] == "approved":
                assert d["allocated"] is not None, (
                    f"{d['request_id']} approved without allocation"
                )

    def test_rejected_has_no_allocation(self, decisions):
        for d in decisions:
            if d["status"] == "rejected":
                assert d["allocated"] is None, (
                    f"{d['request_id']} rejected but carries allocation"
                )

    def test_alternative_has_alternative_slot(self, decisions):
        for d in decisions:
            if d["status"] == "alternative_offered":
                assert d["alternative"] is not None, (
                    f"{d['request_id']} alternative_offered but no slot"
                )


# ── 9. No double-booking ───────────────────────────────────────


class TestNoDoubleBooking:
    def test_no_room_period_overlap(self, decisions):
        """No two allocated bookings occupy the same (room, day, period)."""
        occupied: dict[tuple[str, str, int], str] = {}
        for d in decisions:
            slot = d.get("allocated") or d.get("alternative")
            if slot is None:
                continue
            rid = slot["room_id"]
            day = slot["day"]
            for p in range(slot["start_period"], slot["end_period"] + 1):
                key = (rid, day, p)
                assert key not in occupied, (
                    f"Double booking at {key}: "
                    f"{occupied[key]} and {d['request_id']}"
                )
                occupied[key] = d["request_id"]


# ── 10. Alternative-room offering ──────────────────────────────


class TestAlternativeOffering:
    def test_invalid_room_id_gets_alternative(self, decision_map):
        """BR-14 requests 'LHC-5' (doesn't exist) → alternative offered."""
        d = decision_map["BR-14"]
        # Should get an alternative or at least not crash
        assert d["status"] in ("alternative_offered", "approved")
        if d["status"] == "alternative_offered":
            assert d["alternative"] is not None


# ── 11. Room-feature validation ─────────────────────────────────


class TestRoomFeatures:
    def test_allocated_rooms_have_required_features(self, decisions):
        """Every allocated room must carry all features the request needs."""
        ds = load_dataset()
        room_by_id = {r["id"]: r for r in ds["rooms"]}
        br_map = {br["id"]: br for br in ds["booking_requests"]}

        for d in decisions:
            slot = d.get("allocated") or d.get("alternative")
            if slot is None:
                continue
            br = br_map.get(d["request_id"])
            if not br:
                continue
            room = room_by_id[slot["room_id"]]
            room_feats = set(room.get("features", []))
            for feat in br.get("needs", []):
                if feat == "accessible":
                    assert room.get("accessible", False), (
                        f"{d['request_id']}: room {slot['room_id']} "
                        "is not accessible"
                    )
                else:
                    assert feat in room_feats, (
                        f"{d['request_id']}: room {slot['room_id']} "
                        f"missing feature '{feat}'"
                    )


# ── 12. Room capacity on allocated bookings ─────────────────────


class TestAllocatedCapacity:
    def test_allocated_room_capacity_sufficient(self, decisions):
        ds = load_dataset()
        room_by_id = {r["id"]: r for r in ds["rooms"]}
        br_map = {br["id"]: br for br in ds["booking_requests"]}

        for d in decisions:
            slot = d.get("allocated") or d.get("alternative")
            if slot is None:
                continue
            br = br_map.get(d["request_id"])
            if not br:
                continue
            room = room_by_id[slot["room_id"]]
            assert room["capacity"] >= br["attendance"], (
                f"{d['request_id']}: room {slot['room_id']} "
                f"cap {room['capacity']} < attendance {br['attendance']}"
            )


# ── 13. Route registration ─────────────────────────────────────


class TestRouteRegistration:
    def test_booking_routes_registered(self):
        from app.main import app

        schema = app.openapi()
        assert "/api/bookings/process" in schema["paths"]
        assert "/api/bookings/validate" in schema["paths"]

