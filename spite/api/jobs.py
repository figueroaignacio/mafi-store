from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from spite.db import crud
from spite.db.engine import get_db
from spite.db.models import Job, JobStatus

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    url: str
    platform: str
    location: str | None
    salary: str | None
    score: float | None
    score_summary: str | None = None
    score_reasoning: str | None = None
    red_flags: list[str] | None = None
    green_flags: list[str] | None = None
    status: str

    model_config = {"from_attributes": True}


class StatusUpdate(BaseModel):
    status: JobStatus


@router.get("/", response_model=list[JobResponse])
def list_jobs(
    min_score: float | None = None,
    status: JobStatus | None = None,
    platform: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List all saved jobs with optional filters."""
    return crud.get_jobs(
        db, min_score=min_score, status=status, platform=platform, limit=limit
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a single job by ID."""
    job = crud.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=404, detail="Job not found. Like most opportunities."
        )
    return job


@router.patch("/{job_id}/status", response_model=JobResponse)
def update_status(job_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    """Update job status (applied, ignored, etc)."""
    job = crud.update_job_status(db, job_id, body.status)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job. Sometimes that's the right call."""
    job = crud.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    db.delete(job)
    db.commit()
    return {"message": f"Job {job_id} deleted. Good riddance."}


@router.delete("/")
def delete_all_jobs(db: Session = Depends(get_db)):
    """Delete all jobs. No survivors."""
    count = db.query(Job).count()
    db.query(Job).delete()
    db.commit()
    return {"message": f"Deleted {count} jobs. The market was garbage anyway."}
