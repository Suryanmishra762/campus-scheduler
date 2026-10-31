"""Pydantic models for the venue booking system."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DecisionStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    ALTERNATIVE_OFFERED = "alternative_offered"


class TimeWindow(BaseModel):
    day: str
    from_period: int
    to_period: int


class BookingRequestIn(BaseModel):
    """Schema for validating a single booking request via the API."""

    id: str
    title: str
    requester: str
    role: str
    department: Optional[str] = None
    requested_category: str
    attendance: int
    duration_periods: int
    windows: list[TimeWindow]
    room_types: list[str]
    needs: list[str] = Field(default_factory=list)
    requested_room: Optional[str] = None
    mandatory_for_groups: list[str] = Field(default_factory=list)
    series_id: Optional[str] = None
    submitted_at: str = ""
    raw_text: str = ""


class AllocatedSlot(BaseModel):
    room_id: str
    day: str
    start_period: int
    end_period: int


class BookingDecision(BaseModel):
    request_id: str
    title: str
    requester: str
    status: DecisionStatus
    allocated: Optional[AllocatedSlot] = None
    alternative: Optional[AllocatedSlot] = None
    reasons: list[str] = Field(default_factory=list)

