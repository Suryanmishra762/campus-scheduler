"""
AI Service layer combining Gemini LLM reasoning with deterministic engine checks.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.ai.client import call_gemini, parse_booking_fallback
from app.ai.prompts import (
    BOOKING_EXTRACTION_SYSTEM_PROMPT,
    DECISION_EXPLANATION_PROMPT,
    SCHEDULE_CHANGE_SYSTEM_PROMPT,
)
from app.core.dataset import load_dataset
from app.rescheduling.engine import generate_proposal

logger = logging.getLogger(__name__)


def parse_booking_prompt(text: str, user: dict) -> dict[str, Any]:
    """Parse English / Hinglish booking text into a structured booking request.

    Uses Gemini API if available, with automatic rule-based fallback.
    """
    raw_response = call_gemini(
        prompt=f"User request: '{text}'",
        system_instruction=BOOKING_EXTRACTION_SYSTEM_PROMPT,
        temperature=0.1,
    )

    result = None
    if raw_response:
        try:
            # Strip markdown json codeblocks if returned
            clean_json = raw_response.strip()
            if clean_json.startswith("```"):
                clean_json = re.sub(r"^```[a-zA-Z]*\n", "", clean_json)
                clean_json = re.sub(r"\n```$", "", clean_json)
            result = json.loads(clean_json)
        except Exception as exc:
            logger.warning("Failed to parse Gemini booking JSON (%s). Using fallback.", exc)

    if not result:
        result = parse_booking_fallback(text, user)

    # Ensure required structure
    result.setdefault("title", "Venue Booking")
    result.setdefault("attendance", 40)
    result.setdefault("duration_periods", 1)
    result.setdefault("windows", [{"day": "MON", "from_period": 10, "to_period": 11}])
    result.setdefault("needs", [])
    result.setdefault("room_types", ["classroom", "seminar_hall"])
    result.setdefault("mandatory_for_groups", [])
    result.setdefault("follow_up", None)
    result["raw_text"] = text

    # Set appropriate category based on user role
    role = user.get("role", "faculty")
    role_category_defaults = {
        "admin": "institute_event",
        "faculty": "guest_lecture",
        "department_coordinator": "department_event",
        "club": "club_event",
    }
    result["requested_category"] = role_category_defaults.get(role, "club_event")

    return result


def process_ai_reschedule_request(prompt: str, user: dict) -> dict[str, Any]:
    """Translate natural language request into a disruption and generate a proposal.

    Rule: Gemini NEVER alters schedules directly; all proposals run through CP-SAT.
    """
    fac_id = user.get("faculty_id") or "F01"

    # Attempt Gemini extraction
    gemini_out = call_gemini(
        prompt=f"Faculty {fac_id} requests: '{prompt}'",
        system_instruction=SCHEDULE_CHANGE_SYSTEM_PROMPT,
        temperature=0.1,
    )

    changes = []
    description = prompt

    if gemini_out:
        try:
            clean = gemini_out.strip()
            if clean.startswith("```"):
                clean = re.sub(r"^```[a-zA-Z]*\n", "", clean)
                clean = re.sub(r"\n```$", "", clean)
            parsed = json.loads(clean)
            changes = parsed.get("changes", [])
            description = parsed.get("description", prompt)
        except Exception:
            pass

    # Deterministic fallback disruption parsing if Gemini not available or empty
    if not changes:
        t_low = prompt.lower()
        day_map = {
            "monday": "MON", "tuesday": "TUE", "wednesday": "WED",
            "thursday": "THU", "friday": "FRI",
        }
        target_day = "MON"
        for k, v in day_map.items():
            if k in t_low:
                target_day = v
                break

        if "leave" in t_low or "unavailable" in t_low:
            changes.append({
                "type": "faculty_unavailable",
                "faculty_id": fac_id,
                "days": [target_day],
                "periods": [1, 2, 3, 4, 5, 6, 7, 8, 9],
                "reason": prompt,
            })
            description = f"Faculty {fac_id} unavailable on {target_day}"
        elif "maintenance" in t_low or "closed" in t_low:
            room_match = re.search(r"\b(cr-10[1-6]|lh-[1-5]|sh-[1-3]|aud)\b", t_low)
            rid = room_match.group(1).upper() if room_match else "CR-101"
            changes.append({
                "type": "room_unavailable",
                "room_id": rid,
                "days": [target_day],
                "periods": [1, 2, 3, 4],
                "reason": prompt,
            })
            description = f"Room {rid} maintenance on {target_day}"
        else:
            # Default mock addition
            changes.append({
                "type": "faculty_unavailable",
                "faculty_id": fac_id,
                "days": [target_day],
                "periods": [1, 2],
                "reason": prompt,
            })

    # Execute deterministic CP-SAT proposal solver (minimal moves)
    proposal = generate_proposal(changes, time_limit_seconds=60)

    return {
        "description": description,
        "extracted_changes": changes,
        "proposal_id": proposal.get("proposal_id"),
        "status": proposal.get("status"),
        "solver_status": proposal.get("solver_status"),
        "moved_count": proposal.get("moved_count"),
        "added_count": proposal.get("added_count"),
        "conflicts": proposal.get("conflicts", []),
        "changes": proposal.get("changes", []),
        "approved": False,
        "requires_admin_approval": True,
    }


def explain_decision_ai(decision_type: str, context: dict[str, Any]) -> str:
    """Generate human-readable explanation for a booking or scheduling decision."""
    prompt = (
        f"Explain this {decision_type} decision clearly to a student/faculty member.\n"
        f"Context: {json.dumps(context, default=str)}"
    )

    gemini_out = call_gemini(
        prompt=prompt,
        system_instruction=DECISION_EXPLANATION_PROMPT,
        temperature=0.3,
    )

    if gemini_out and len(gemini_out.strip()) > 10:
        return gemini_out.strip()

    # Deterministic fallback explanations
    reasons = context.get("reasons", [])
    status = context.get("status", "")

    if status == "rejected":
        reason_str = "; ".join(reasons) if reasons else "Venue capacity or time-window conflict."
        return (
            f"Your booking could not be approved due to the following constraint: {reason_str}. "
            f"Please check alternative available venues or choose a different time window."
        )
    elif status == "alternative_offered":
        alt = context.get("alternative", {})
        alt_room = alt.get("room_id", "an alternative room")
        return (
            f"Your requested venue was unavailable due to existing priority allocations, "
            f"but {alt_room} has been offered as an alternative that fits your capacity and needs."
        )
    elif status == "approved":
        return "Your booking request satisfies all campus venue policies, capacity limits, and time-window constraints."

    return "Decision evaluated according to CIT Campus scheduling and venue allocation policies."

