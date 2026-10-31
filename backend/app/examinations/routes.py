"""API routes for the exam scheduling system."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.examinations.engine import schedule_exams

router = APIRouter(prefix="/api/exams", tags=["exams"])


@router.post("/schedule")
def generate_exam_schedule():
    """Run the deterministic exam scheduler and return the result.

    Schedules all exams from the dataset into exam-week slots
    (Mon–Sat, AM/PM) using half seating capacity with multi-room
    allocation.  Returns scheduled exams, unscheduled exams, and
    summary counts.
    """
    try:
        result = schedule_exams()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Exam scheduling error: {exc}",
        )

    return result


@router.get("/schedule")
def get_exam_schedule():
    """Retrieve the exam schedule (re-generates deterministically)."""
    try:
        result = schedule_exams()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Exam scheduling error: {exc}",
        )

    return result

