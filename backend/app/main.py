"""
CIT Campus Scheduler API — FastAPI application.

Lifespan handler initialises JWKS at startup (fails if unreachable
for RS256/ES256 mode).  All routes are included via routers.
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException

from app.core.auth import get_verified_user, init_jwks
from app.core.dataset import load_dataset, get_dataset_summary
from app.core.permissions import require_admin_or_coord
from app.scheduling.routes import router as schedule_router
from app.bookings.routes import router as booking_router
from app.examinations.routes import router as exam_router
from app.rescheduling.routes import router as reschedule_router
from app.admin.routes import router as admin_router
from app.ai.routes import router as ai_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialise JWKS on startup."""
    init_jwks()
    yield


app = FastAPI(
    title="CIT Campus Scheduler API",
    description="Campus Scheduling and Venue Management System",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(schedule_router)
app.include_router(booking_router)
app.include_router(exam_router)
app.include_router(reschedule_router)
app.include_router(admin_router)
app.include_router(ai_router)


@app.get("/")
def root():
    return {"message": "CIT Campus Scheduler API is running", "status": "healthy"}


@app.get("/api/me")
def get_current_user_profile(user: dict = Depends(get_verified_user)):
    """Return the authenticated user's profile."""
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user.get("full_name", ""),
        "role": user.get("role", "faculty"),
        "department": user.get("department"),
        "faculty_id": user.get("faculty_id"),
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "CIT Campus Scheduler Backend"}


@app.get("/api/dataset/summary")
def dataset_summary():
    try:
        return get_dataset_summary()
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/api/dataset")
def dataset_info():
    try:
        dataset = load_dataset()
        return {
            "dataset_id": dataset["dataset_id"],
            "institute": dataset["institute"],
            "calendar": dataset["calendar"],
            "counts": get_dataset_summary()["counts"],
        }
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/api/dataset/full")
def dataset_full(user: dict = Depends(require_admin_or_coord)):
    """Full dataset — restricted to admin and department coordinators."""
    try:
        dataset = load_dataset()
        return {
            "rooms": dataset["rooms"],
            "faculty": dataset["faculty"],
            "student_groups": dataset["student_groups"],
            "courses": dataset["courses"],
            "sessions": dataset["sessions"],
            "booking_requests": dataset["booking_requests"],
            "exams": dataset["exams"],
        }
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=500, detail=str(error))
