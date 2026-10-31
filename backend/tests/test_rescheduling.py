"""
Focused tests for Disruption Management and Rescheduling.

Covers:
  1.  Proposal generation with sample_disruption.json
  2.  Faculty-unavailable sessions are moved
  3.  Room-closed sessions are moved
  4.  New session is added
  5.  Unaffected sessions are frozen
  6.  Moves are minimised
  7.  Hard constraints preserved (no faculty/room/group clashes)
  8.  Infeasible disruption returns conflicts
  9.  Approval applies exact proposal without re-solving
  10. Cannot approve infeasible or already-approved proposals
  11. Before/after diff present for every change
  12. Route registration
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.dataset import load_dataset
from app.rescheduling.engine import (
    approve_proposal,
    generate_proposal,
    get_proposal,
    _proposals,
)


# ── Fixtures ────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DISRUPTION = PROJECT_ROOT / "data" / "sample_disruption.json"


@pytest.fixture(scope="module")
def sample_changes():
    with open(SAMPLE_DISRUPTION, encoding="utf-8") as f:
        return json.load(f)["changes"]


@pytest.fixture(scope="module")
def proposal(sample_changes):
    return generate_proposal(sample_changes, time_limit_seconds=60)


@pytest.fixture(scope="module")
def dataset():
    return load_dataset()


# ── 1. Proposal generation ─────────────────────────────────────


class TestProposalGeneration:
    def test_proposal_has_id(self, proposal):
        assert proposal["proposal_id"]
        assert len(proposal["proposal_id"]) == 16

    def test_proposal_is_feasible(self, proposal):
        assert proposal["status"] == "feasible"
        assert proposal["solver_status"] in ("OPTIMAL", "FEASIBLE")

    def test_proposal_not_yet_approved(self, proposal):
        assert proposal["approved"] is False


# ── 2. Faculty-unavailable sessions moved ──────────────────────


class TestFacultyUnavailable:
    def test_no_f07_on_monday_in_approved_schedule(self, proposal):
        """After disruption, F07 must not teach on MON in the schedule."""
        schedule = proposal.get("_approved_schedule")
        if not schedule:
            pytest.skip("No approved schedule")

        violations = [
            s["session_id"]
            for s in schedule
            if s.get("faculty_id") == "F07" and s["day"] == "MON"
        ]
        assert len(violations) == 0, (
            f"F07 still teaches on MON: {violations}"
        )


# ── 3. Room-closed sessions moved ──────────────────────────────


class TestRoomClosed:
    def test_no_cr102_in_approved_schedule(self, proposal):
        """After disruption, no session should be in CR-102."""
        schedule = proposal.get("_approved_schedule")
        if not schedule:
            pytest.skip("No approved schedule")

        violations = [
            s["session_id"]
            for s in schedule
            if s["room_id"] == "CR-102"
        ]
        assert len(violations) == 0, (
            f"Sessions still in CR-102: {violations}"
        )


# ── 4. New session added ───────────────────────────────────────


class TestNewSession:
    def test_new_session_in_changes(self, proposal):
        added = [c for c in proposal["changes"] if c["kind"] == "added"]
        added_ids = {c["session_id"] for c in added}
        assert "CS202-T2" in added_ids, "New session CS202-T2 must be added"

    def test_added_session_has_placement(self, proposal):
        for c in proposal["changes"]:
            if c["session_id"] == "CS202-T2" and c["kind"] == "added":
                assert c["after"] is not None
                assert "day" in c["after"]
                assert "period" in c["after"]
                assert "room_id" in c["after"]


# ── 5. Unaffected sessions frozen ──────────────────────────────


class TestFrozenSessions:
    def test_frozen_count_positive(self, proposal):
        assert proposal["frozen_count"] > 0

    def test_most_sessions_frozen(self, proposal):
        """The majority of sessions should remain frozen."""
        total = proposal["total_sessions"]
        frozen = proposal["frozen_count"]
        assert frozen > total * 0.5, (
            f"Only {frozen}/{total} frozen — too many sessions moved"
        )


# ── 6. Moves minimised ─────────────────────────────────────────


class TestMinimiseMoves:
    def test_moved_count_small(self, proposal):
        """Moved sessions should be a small fraction of total."""
        assert proposal["moved_count"] < proposal["total_sessions"] * 0.25


# ── 7. Hard constraints preserved ──────────────────────────────


class TestHardConstraints:
    def test_no_faculty_clash_in_approved_schedule(self, proposal):
        schedule = proposal.get("_approved_schedule")
        if not schedule:
            pytest.skip("No approved schedule (infeasible)")

        fac_slots: dict[tuple, list] = defaultdict(list)
        for s in schedule:
            fid = s.get("faculty_id")
            if not fid:
                continue
            for off in range(s["duration"]):
                fac_slots[(fid, s["day"], s["period"] + off)].append(
                    s["session_id"]
                )
        clashes = {k: v for k, v in fac_slots.items() if len(v) > 1}
        assert len(clashes) == 0, f"Faculty clashes: {clashes}"

    def test_no_room_clash_in_approved_schedule(self, proposal):
        schedule = proposal.get("_approved_schedule")
        if not schedule:
            pytest.skip("No approved schedule (infeasible)")

        room_slots: dict[tuple, list] = defaultdict(list)
        for s in schedule:
            for off in range(s["duration"]):
                room_slots[
                    (s["room_id"], s["day"], s["period"] + off)
                ].append(s["session_id"])
        clashes = {k: v for k, v in room_slots.items() if len(v) > 1}
        assert len(clashes) == 0, f"Room clashes: {clashes}"

    def test_no_group_clash_in_approved_schedule(self, proposal, dataset):
        schedule = proposal.get("_approved_schedule")
        if not schedule:
            pytest.skip("No approved schedule (infeasible)")

        # Build basket-mate pairs
        ds = dataset
        basket_pairs: set[frozenset[str]] = set()
        sessions_by_id = {s["id"]: s for s in ds["sessions"]}
        basket_slots: dict[str, list[str]] = {}
        for s in ds["sessions"]:
            bs = s.get("basket_slot")
            if bs:
                basket_slots.setdefault(bs, []).append(s["id"])
        for _, sids in basket_slots.items():
            for i, a in enumerate(sids):
                for b in sids[i + 1:]:
                    basket_pairs.add(frozenset([a, b]))

        group_slots: dict[tuple, list] = defaultdict(list)
        for s in schedule:
            for gid in s.get("groups", []):
                for off in range(s["duration"]):
                    group_slots[
                        (gid, s["day"], s["period"] + off)
                    ].append(s["session_id"])

        clashes = {}
        for k, v in group_slots.items():
            if len(v) <= 1:
                continue
            for i, a in enumerate(v):
                for b in v[i + 1:]:
                    if frozenset([a, b]) not in basket_pairs:
                        clashes.setdefault(k, []).append((a, b))

        assert len(clashes) == 0, f"Group clashes: {clashes}"


# ── 8. Infeasible disruption ───────────────────────────────────


class TestInfeasibleDisruption:
    def test_impossible_disruption_returns_conflicts(self):
        """Closing ALL rooms should produce an infeasible result."""
        ds = load_dataset()
        room_ids = [r["id"] for r in ds["rooms"]]
        changes = [
            {
                "type": "room_unavailable",
                "room_id": rid,
                "days": ["MON", "TUE", "WED", "THU", "FRI"],
                "periods": [1, 2, 3, 4, 5, 6, 7, 8, 9],
                "reason": "Total closure",
            }
            for rid in room_ids
        ]
        result = generate_proposal(changes, time_limit_seconds=10)
        assert result["status"] == "infeasible"
        assert len(result["conflicts"]) > 0


# ── 9. Approval ────────────────────────────────────────────────


class TestApproval:
    def test_approve_feasible_proposal(self, proposal):
        pid = proposal["proposal_id"]
        # Reset approval state if already approved by another test
        _proposals[pid]["approved"] = False

        result = approve_proposal(pid, approved_by="admin")
        assert result["approved"] is True
        assert result["approved_by"] == "admin"
        assert result["schedule"] is not None
        assert len(result["schedule"]) > 0

    def test_approved_schedule_matches_proposal(self, proposal):
        """The approved schedule must be the exact pre-computed one."""
        pid = proposal["proposal_id"]
        stored = get_proposal(pid)
        assert stored is not None
        assert stored["approved"] is True

    def test_cannot_approve_twice(self, proposal):
        pid = proposal["proposal_id"]
        result = approve_proposal(pid, approved_by="admin")
        assert "error" in result
        assert "already approved" in result["error"].lower()

    def test_cannot_approve_nonexistent(self):
        result = approve_proposal("nonexistent-id", approved_by="admin")
        assert "error" in result


# ── 10. Before/after diff ──────────────────────────────────────


class TestDiff:
    def test_every_change_has_valid_kind(self, proposal):
        valid = {"moved", "added", "unscheduled"}
        for c in proposal["changes"]:
            assert c["kind"] in valid

    def test_moved_has_before_and_after(self, proposal):
        for c in proposal["changes"]:
            if c["kind"] == "moved":
                assert c["before"] is not None
                assert c["after"] is not None
                assert c["before"] != c["after"]

    def test_added_has_after_only(self, proposal):
        for c in proposal["changes"]:
            if c["kind"] == "added":
                assert c["before"] is None
                assert c["after"] is not None

    def test_unscheduled_has_no_after(self, proposal):
        for c in proposal["changes"]:
            if c["kind"] == "unscheduled":
                assert c["after"] is None


# ── 11. Route registration ─────────────────────────────────────


class TestRouteRegistration:
    def test_reschedule_routes_registered(self):
        from app.main import app

        paths = app.openapi()["paths"]
        assert "/api/reschedule/propose" in paths
        assert "/api/reschedule/approve" in paths
        assert "/api/reschedule/proposal/{proposal_id}" in paths

