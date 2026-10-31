"""API routes for disruption management and rescheduling."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.rescheduling.engine import (
    approve_proposal,
    generate_proposal,
    get_proposal,
)
from app.rescheduling.models import DisruptionInput

router = APIRouter(prefix="/api/reschedule", tags=["rescheduling"])


@router.post("/propose")
def propose_reschedule(
    disruption: DisruptionInput,
    time_limit_seconds: int = 60,
):
    """Generate a rescheduling proposal for the given disruptions.

    Does NOT apply any changes — the proposal must be explicitly
    approved via ``POST /api/reschedule/approve``.
    """
    try:
        proposal = generate_proposal(
            disruption.changes,
            time_limit_seconds=time_limit_seconds,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Rescheduling error: {exc}",
        )

    # Strip internal fields from the response
    return {
        k: v for k, v in proposal.items() if not k.startswith("_")
    }


@router.get("/proposal/{proposal_id}")
def get_proposal_by_id(proposal_id: str):
    """Retrieve a previously generated proposal."""
    proposal = get_proposal(proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return {
        k: v for k, v in proposal.items() if not k.startswith("_")
    }


@router.post("/approve")
def approve_reschedule(
    proposal_id: str,
    approved_by: str = "admin",
):
    """Approve a previously generated and validated rescheduling proposal.

    Applies the exact schedule from the proposal without re-running
    the solver.  Only admins should call this endpoint.
    """
    result = approve_proposal(proposal_id, approved_by)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

