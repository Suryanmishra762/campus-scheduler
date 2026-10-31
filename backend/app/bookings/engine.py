"""
Deterministic Venue Booking and Approval Engine.

Validates booking requests against:
  - Room capacity, type, features, accessibility
  - Time-window availability and calendar period validity
  - Room unavailability schedule
  - Role-based category permissions  (role_category_cap)
  - Booking priority ordering        (priority_order)
  - Cancellation status
  - Self-approval prevention

Returns ``approved``, ``rejected``, or ``alternative_offered`` for every
request.  No LLM or non-deterministic logic is used.
"""

from __future__ import annotations

from typing import Any, Optional

from app.core.dataset import load_dataset


# ── Context builder ─────────────────────────────────────────────


def _build_context() -> dict[str, Any]:
    """Load the dataset and build lookup structures."""
    ds = load_dataset()

    rooms = ds["rooms"]
    room_by_id: dict[str, dict] = {r["id"]: r for r in rooms}

    room_unavail: set[tuple[str, str, int]] = set()
    for ru in ds["room_unavailability"]:
        for pid in ru["periods"]:
            room_unavail.add((ru["room_id"], ru["day"], pid))

    cancelled_ids: set[str] = {c["request_id"] for c in ds["cancellations"]}
    all_period_ids: set[int] = {p["id"] for p in ds["calendar"]["periods"]}

    return {
        "rooms": rooms,
        "room_by_id": room_by_id,
        "room_unavail": room_unavail,
        "cancelled_ids": cancelled_ids,
        "priority_order": ds["priority_order"],
        "role_category_cap": ds["role_category_cap"],
        "all_period_ids": all_period_ids,
        "booking_requests": ds["booking_requests"],
    }


# ── Validation helpers ──────────────────────────────────────────


def check_role_permission(
    role: str,
    requested_category: str,
    priority_order: list[str],
    role_category_cap: dict[str, str],
) -> Optional[str]:
    """Return an error message if the role may not book the category, else *None*.

    A role's *cap* is the highest-priority category it may request.
    Categories with a *lower* index in ``priority_order`` are higher
    priority and therefore above the cap.
    """
    if role not in role_category_cap:
        return f"Unknown role '{role}'"
    if requested_category not in priority_order:
        return f"Unknown category '{requested_category}'"

    cap_idx = priority_order.index(role_category_cap[role])
    req_idx = priority_order.index(requested_category)

    if req_idx < cap_idx:
        return (
            f"Role '{role}' cannot book category '{requested_category}'; "
            f"maximum allowed is '{role_category_cap[role]}'"
        )
    return None


def find_candidate_rooms(
    br: dict,
    rooms: list[dict],
) -> list[dict]:
    """Return rooms that satisfy type, capacity, features, and accessibility."""
    needs = br.get("needs", [])
    needs_accessible = "accessible" in needs
    required_features = [f for f in needs if f != "accessible"]

    candidates: list[dict] = []
    for room in rooms:
        # Type check
        if room["type"] not in br["room_types"]:
            continue
        # Capacity check
        if room["capacity"] < br["attendance"]:
            continue
        # Accessibility check
        if needs_accessible and not room.get("accessible", False):
            continue
        # Feature check
        room_features = set(room.get("features", []))
        if not all(f in room_features for f in required_features):
            continue
        # Booking requests are events; room must allow "event"
        if "event" not in room.get("allowed_uses", []):
            continue
        candidates.append(room)
    return candidates


def find_available_slots(
    br: dict,
    room: dict,
    room_unavail: set[tuple[str, str, int]],
    allocated: dict[tuple[str, str, int], str],
    all_period_ids: set[int],
) -> list[tuple[str, int]]:
    """Return ``(day, start_period)`` pairs where the booking fits."""
    duration = br["duration_periods"]
    results: list[tuple[str, int]] = []

    for window in br["windows"]:
        day: str = window["day"]
        fp: int = window["from_period"]
        tp: int = window["to_period"]

        max_start = tp - duration + 1
        for start in range(fp, max_start + 1):
            periods = range(start, start + duration)
            # Every occupied period must exist in the calendar
            if not all(p in all_period_ids for p in periods):
                continue
            # Must not overlap with room unavailability
            if any((room["id"], day, p) in room_unavail for p in periods):
                continue
            # Must not overlap with already-allocated slots
            if any((room["id"], day, p) in allocated for p in periods):
                continue
            results.append((day, start))

    return results


# ── Single-request decision ─────────────────────────────────────


def _decide(
    br: dict,
    priority_order: list[str],
    role_category_cap: dict[str, str],
    rooms: list[dict],
    room_by_id: dict[str, dict],
    room_unavail: set[tuple[str, str, int]],
    allocated: dict[tuple[str, str, int], str],
    cancelled_ids: set[str],
    all_period_ids: set[int],
) -> dict:
    """Return a decision dict for one booking request."""

    reasons: list[str] = []
    base = {
        "request_id": br["id"],
        "title": br["title"],
        "requester": br["requester"],
    }

    # ── Gate 1: cancelled request ──
    if br["id"] in cancelled_ids:
        return {
            **base,
            "status": "rejected",
            "reasons": [f"Request '{br['id']}' has been cancelled"],
            "allocated": None,
            "alternative": None,
        }

    # ── Gate 2: role-category permission ──
    perm_err = check_role_permission(
        br["role"],
        br["requested_category"],
        priority_order,
        role_category_cap,
    )
    if perm_err:
        return {
            **base,
            "status": "rejected",
            "reasons": [perm_err],
            "allocated": None,
            "alternative": None,
        }

    # ── Gate 3: find candidate rooms ──
    candidates = find_candidate_rooms(br, rooms)
    if not candidates:
        return {
            **base,
            "status": "rejected",
            "reasons": [
                "No room matches required type, capacity, features, "
                "and accessibility"
            ],
            "allocated": None,
            "alternative": None,
        }

    # ── Gate 4: split into preferred / alternative lists ──
    requested_room_id = br.get("requested_room")
    preferred: list[dict] = []
    alternatives: list[dict] = []

    if requested_room_id and requested_room_id in room_by_id:
        req_room = room_by_id[requested_room_id]
        if req_room in candidates:
            preferred = [req_room]
            alternatives = [r for r in candidates if r["id"] != requested_room_id]
        else:
            reasons.append(
                f"Requested room '{requested_room_id}' does not meet "
                "type, capacity, feature, or accessibility requirements"
            )
            alternatives = candidates
    elif requested_room_id:
        # Room ID not found in the dataset
        reasons.append(f"Requested room '{requested_room_id}' not found")
        alternatives = candidates
    else:
        alternatives = candidates

    # Prefer the smallest room that still fits (reduce capacity waste)
    alternatives.sort(key=lambda r: r["capacity"])

    # ── Helpers ──
    def _try_allocate(
        room_list: list[dict],
    ) -> Optional[tuple[dict, str, int]]:
        for room in room_list:
            slots = find_available_slots(
                br, room, room_unavail, allocated, all_period_ids,
            )
            if slots:
                return room, slots[0][0], slots[0][1]
        return None

    def _make_slot(room: dict, day: str, start: int) -> dict:
        return {
            "room_id": room["id"],
            "day": day,
            "start_period": start,
            "end_period": start + br["duration_periods"] - 1,
        }

    def _mark_allocated(room: dict, day: str, start: int) -> None:
        for p in range(start, start + br["duration_periods"]):
            allocated[(room["id"], day, p)] = br["id"]

    # ── Try preferred room first ──
    hit = _try_allocate(preferred)
    if hit:
        room, day, start = hit
        _mark_allocated(room, day, start)
        return {
            **base,
            "status": "approved",
            "reasons": reasons or ["All constraints satisfied"],
            "allocated": _make_slot(room, day, start),
            "alternative": None,
        }

    # ── Try alternative rooms ──
    hit = _try_allocate(alternatives)
    if hit:
        room, day, start = hit
        _mark_allocated(room, day, start)
        slot = _make_slot(room, day, start)

        if requested_room_id:
            # The requester asked for a specific room we couldn't use
            reasons.append(
                f"Alternative room '{room['id']}' offered instead"
            )
            return {
                **base,
                "status": "alternative_offered",
                "reasons": reasons,
                "allocated": None,
                "alternative": slot,
            }

        return {
            **base,
            "status": "approved",
            "reasons": reasons or ["All constraints satisfied"],
            "allocated": slot,
            "alternative": None,
        }

    # ── Nothing works ──
    reasons.append("No available time slot in any compatible room")
    return {
        **base,
        "status": "rejected",
        "reasons": reasons,
        "allocated": None,
        "alternative": None,
    }


# ── Public API ──────────────────────────────────────────────────


def process_all_bookings() -> list[dict]:
    """Process every booking request from the dataset.

    Requests are sorted by priority (highest first, per
    ``priority_order``) then by ``submitted_at`` timestamp.
    Higher-priority bookings are allocated first; lower-priority ones
    receive alternatives or rejections when conflicts arise.
    """
    ctx = _build_context()
    po: list[str] = ctx["priority_order"]

    def _sort_key(br: dict) -> tuple[int, str]:
        cat = br["requested_category"]
        idx = po.index(cat) if cat in po else len(po)
        return (idx, br["submitted_at"])

    ordered = sorted(ctx["booking_requests"], key=_sort_key)

    allocated: dict[tuple[str, str, int], str] = {}
    decisions: list[dict] = []

    for br in ordered:
        decision = _decide(
            br,
            po,
            ctx["role_category_cap"],
            ctx["rooms"],
            ctx["room_by_id"],
            ctx["room_unavail"],
            allocated,
            ctx["cancelled_ids"],
            ctx["all_period_ids"],
        )
        decisions.append(decision)

    return decisions


def validate_single_booking(
    request: dict,
    approver: Optional[str] = None,
) -> dict:
    """Validate one booking request in isolation.

    If *approver* is supplied and equals the requester the request is
    rejected (self-approval prevention).
    """
    ctx = _build_context()

    # Self-approval guard
    if approver is not None and approver == request.get("requester"):
        return {
            "request_id": request.get("id", "unknown"),
            "title": request.get("title", ""),
            "requester": request.get("requester", ""),
            "status": "rejected",
            "reasons": ["Self-approval is not allowed"],
            "allocated": None,
            "alternative": None,
        }

    allocated: dict[tuple[str, str, int], str] = {}
    return _decide(
        request,
        ctx["priority_order"],
        ctx["role_category_cap"],
        ctx["rooms"],
        ctx["room_by_id"],
        ctx["room_unavail"],
        allocated,
        ctx["cancelled_ids"],
        ctx["all_period_ids"],
    )

