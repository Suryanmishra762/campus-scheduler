"""Pydantic models for the exam scheduling system."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class RoomAllocation(BaseModel):
    """One room assigned to an exam with the number of seats used."""

    room_id: str
    seats_used: int


class ScheduledExam(BaseModel):
    """An exam that was successfully placed."""

    exam_id: str
    course_ids: list[str]
    groups: list[str]
    size: int
    day: str
    session: str  # "AM" or "PM"
    rooms: list[RoomAllocation]


class UnscheduledExam(BaseModel):
    """An exam that could not be placed."""

    exam_id: str
    reason: str


class ExamScheduleResult(BaseModel):
    """Full result returned by the scheduler."""

    total_exams: int
    scheduled_count: int
    unscheduled_count: int
    scheduled: list[ScheduledExam]
    unscheduled: list[UnscheduledExam]
    slots_used: int
    slots_available: int

