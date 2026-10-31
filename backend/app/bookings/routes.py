"""API routes for the venue booking system."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.bookings.engine import process_all_bookings, validate_single_booking
from app.bookings.models import BookingRequestIn

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.post("/process")
def process_bookings():
    """Process all booking requests from the dataset and return decisions.

    Requests are evaluated in priority order (highest first), then by
    submission timestamp.  Each receives ``approved``, ``rejected``, or
    ``alternative_offered`` with reasons.
    """
    try:
        decisions = process_all_bookings()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Processing error: {exc}",
        )

    summary = {
        "approved": sum(1 for d in decisions if d["status"] == "approved"),
        "rejected": sum(1 for d in decisions if d["status"] == "rejected"),
        "alternative_offered": sum(
            1 for d in decisions if d["status"] == "alternative_offered"
        ),
    }

    return {
        "total": len(decisions),
        "summary": summary,
        "decisions": decisions,
    }


@router.post("/validate")
def validate_booking(
    request: BookingRequestIn,
    approved_by: str | None = None,
):
    """Validate a single booking request.

    If ``approved_by`` is supplied and equals the requester the request
    is rejected (self-approval prevention).
    """
    try:
        decision = validate_single_booking(
            request.model_dump(),
            approver=approved_by,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Validation error: {exc}",
        )

    return decision

