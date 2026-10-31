"""
Deterministic Exam Scheduling Engine.

Schedules all exams from the CIT dataset into the exam-week calendar
(Mon–Sat, AM/PM sessions) using a greedy approach:

  1. Sort exams by descending size (largest first) to allocate the
     hardest-to-place exams while room availability is maximal.
  2. For each exam, iterate over slots in calendar order and pick the
     first slot that has no student-group clash and enough room
     capacity (at half seating) — splitting across multiple rooms when
     a single room is insufficient.
  3. Record scheduled and unscheduled exams with clear reasons.

Constraints enforced:
  - Half seating capacity (``room.capacity // 2``) for exams.
  - Multi-room allocation when one room is not enough.
  - No two exams sharing a student group in the same slot.
  - Only rooms whose ``allowed_uses`` include ``"exam"`` are eligible.
  - Room unavailability during exam week is respected.

No LLM or non-deterministic logic is used.
"""

from __future__ import annotations

from typing import Any

from app.core.dataset import load_dataset


# ── Context ─────────────────────────────────────────────────────


def _build_exam_context() -> dict[str, Any]:
    """Load the dataset and build lookup structures for exam scheduling."""
    ds = load_dataset()

    calendar = ds["calendar"]
    exam_week = calendar["exam_week"]

    # Exam-eligible rooms (allowed_uses includes "exam"), sorted by
    # half-capacity descending so the allocator fills big rooms first.
    exam_rooms = sorted(
        [r for r in ds["rooms"] if "exam" in r.get("allowed_uses", [])],
        key=lambda r: r["capacity"],
        reverse=True,
    )

    # Pre-compute half capacity for each room
    room_half_cap: dict[str, int] = {
        r["id"]: r["capacity"] // 2 for r in exam_rooms
    }

    # Room unavailability — only relevant if it overlaps with exam week
    # The dataset's room_unavailability uses teaching-period ids (1-9)
    # which don't directly map to exam sessions (AM/PM).  We keep the
    # raw data but also build a set of (room_id, day) pairs where a
    # *full-day* closure is recorded (all teaching periods blocked).
    all_teaching = set(p["id"] for p in calendar["periods"] if p["teaching"])
    room_day_unavail: set[tuple[str, str]] = set()
    for ru in ds["room_unavailability"]:
        blocked = set(ru["periods"])
        if all_teaching <= blocked:
            # Room is unavailable for the entire day
            room_day_unavail.add((ru["room_id"], ru["day"]))

    return {
        "exams": ds["exams"],
        "exam_days": exam_week["days"],
        "exam_sessions": exam_week["sessions"],
        "exam_rooms": exam_rooms,
        "room_half_cap": room_half_cap,
        "room_day_unavail": room_day_unavail,
    }


# ── Allocator helpers ───────────────────────────────────────────


def _available_rooms_in_slot(
    day: str,
    session_id: str,
    exam_rooms: list[dict],
    room_half_cap: dict[str, int],
    room_day_unavail: set[tuple[str, str]],
    slot_room_usage: dict[tuple[str, str, str], str],
) -> list[tuple[str, int]]:
    """Return ``[(room_id, half_capacity)]`` for rooms free in this slot."""
    free: list[tuple[str, int]] = []
    for r in exam_rooms:
        rid = r["id"]
        if (rid, day) in room_day_unavail:
            continue
        if (rid, day, session_id) in slot_room_usage:
            continue
        free.append((rid, room_half_cap[rid]))
    return free


def _allocate_rooms(
    needed: int,
    available: list[tuple[str, int]],
) -> list[tuple[str, int]] | None:
    """Greedily pick rooms (largest first) until *needed* seats are covered.

    Returns a list of ``(room_id, seats_used)`` or ``None`` if the
    available capacity is insufficient.
    """
    picked: list[tuple[str, int]] = []
    remaining = needed
    for rid, cap in available:
        if remaining <= 0:
            break
        use = min(cap, remaining)
        picked.append((rid, use))
        remaining -= use
    if remaining > 0:
        return None
    return picked


# ── Main scheduler ──────────────────────────────────────────────


def schedule_exams() -> dict[str, Any]:
    """Schedule all 41 exams and return a result dict.

    The algorithm is deterministic:
      1. Exams sorted by size descending (ties broken by id).
      2. Slots iterated in calendar order (Mon-AM, Mon-PM, Tue-AM, …).
      3. First feasible slot (no group clash, enough room capacity) wins.
    """
    ctx = _build_exam_context()

    exams = ctx["exams"]
    days = ctx["exam_days"]
    sessions = ctx["exam_sessions"]
    exam_rooms = ctx["exam_rooms"]
    room_half_cap = ctx["room_half_cap"]
    room_day_unavail = ctx["room_day_unavail"]

    # All (day, session_id) slots in calendar order
    slots: list[tuple[str, str]] = [
        (day, sess["id"]) for day in days for sess in sessions
    ]

    # Sort exams: largest first, then by id for determinism
    sorted_exams = sorted(exams, key=lambda e: (-e["size"], e["id"]))

    # Tracking structures
    # group_slot: (group_id, day, session_id) -> exam_id  (clash detection)
    group_slot: dict[tuple[str, str, str], str] = {}
    # room_slot: (room_id, day, session_id) -> exam_id
    slot_room_usage: dict[tuple[str, str, str], str] = {}

    scheduled: list[dict] = []
    unscheduled: list[dict] = []

    for exam in sorted_exams:
        eid = exam["id"]
        groups = exam["groups"]
        size = exam["size"]
        placed = False

        for day, sess_id in slots:
            # ── Group-clash check ──
            clash = False
            for gid in groups:
                if (gid, day, sess_id) in group_slot:
                    clash = True
                    break
            if clash:
                continue

            # ── Room availability and allocation ──
            available = _available_rooms_in_slot(
                day, sess_id, exam_rooms, room_half_cap,
                room_day_unavail, slot_room_usage,
            )
            allocation = _allocate_rooms(size, available)
            if allocation is None:
                continue

            # ── Commit ──
            for gid in groups:
                group_slot[(gid, day, sess_id)] = eid
            for rid, seats in allocation:
                slot_room_usage[(rid, day, sess_id)] = eid

            scheduled.append({
                "exam_id": eid,
                "course_ids": exam["course_ids"],
                "groups": groups,
                "size": size,
                "day": day,
                "session": sess_id,
                "rooms": [
                    {"room_id": rid, "seats_used": seats}
                    for rid, seats in allocation
                ],
            })
            placed = True
            break

        if not placed:
            unscheduled.append({
                "exam_id": eid,
                "reason": "No slot with sufficient room capacity and no group clash",
            })

    # Count distinct slots used
    slots_used = len({
        (s["day"], s["session"]) for s in scheduled
    })

    return {
        "total_exams": len(exams),
        "scheduled_count": len(scheduled),
        "unscheduled_count": len(unscheduled),
        "scheduled": scheduled,
        "unscheduled": unscheduled,
        "slots_used": slots_used,
        "slots_available": len(slots),
    }

