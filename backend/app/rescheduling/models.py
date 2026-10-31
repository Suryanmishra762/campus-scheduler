"""Pydantic models for the disruption / rescheduling system."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Disruption input ────────────────────────────────────────────


class FacultyUnavailableChange(BaseModel):
    type: str = "faculty_unavailable"
    faculty_id: str
    days: list[str]
    periods: list[int]
    reason: str = ""


class RoomUnavailableChange(BaseModel):
    type: str = "room_unavailable"
    room_id: str
    days: list[str]
    periods: list[int]
    reason: str = ""


class AddSessionChange(BaseModel):
    type: str = "add_session"
    session: dict


class DisruptionInput(BaseModel):
    """Top-level disruption payload (mirrors ``sample_disruption.json``)."""

    id: str = ""
    dataset: str = ""
    description: str = ""
    changes: list[dict]


# ── Proposal output ─────────────────────────────────────────────


class ChangeKind(str, Enum):
    MOVED = "moved"
    ADDED = "added"
    UNSCHEDULED = "unscheduled"


class SessionChange(BaseModel):
    session_id: str
    kind: ChangeKind
    before: Optional[dict] = None   # {day, period, room_id}
    after: Optional[dict] = None    # {day, period, room_id}
    reason: str = ""


class RescheduleProposal(BaseModel):
    proposal_id: str
    status: str                     # "feasible" | "infeasible"
    solver_status: str              # "OPTIMAL" | "FEASIBLE" | …
    total_sessions: int
    frozen_count: int
    rescheduled_count: int
    moved_count: int
    added_count: int
    unscheduled_count: int
    changes: list[SessionChange]
    conflicts: list[str] = Field(default_factory=list)
    solve_time_seconds: float = 0.0
    approved: bool = False

