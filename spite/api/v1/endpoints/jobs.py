from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from spite.api.dependencies import get_db
from spite.models.job import JobStatus
from spite.repositories.job_repository import job_repository
from spite.schemas.job import JobResponse, JobUpdate, StatusUpdate

router = APIRouter()


@router.get("/", response_model=list[JobResponse])
async def list_jobs(
    status: JobStatus | None = None,
    platform: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List all saved jobs with optional filters."""
    return await job_repository.get_jobs_with_filters(
        db, status=status, platform=platform, limit=limit
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single job by ID."""
    job = await job_repository.get(db, job_id)
    if not job:
        raise HTTPException(
            status_code=404, detail="Job not found. Like most opportunities."
        )
    return job


@router.patch("/{job_id}/status", response_model=JobResponse)
async def update_status(
    job_id: int, body: StatusUpdate, db: AsyncSession = Depends(get_db)
):
    """Update job status (applied, ignored, etc)."""
    job = await job_repository.get(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return await job_repository.update(db, job, JobUpdate(status=body.status))


@router.delete("/{job_id}")
async def delete_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a job. Sometimes that's the right call."""
    deleted = await job_repository.delete(db, job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found.")
    await db.commit()
    return {"message": f"Job {job_id} deleted. Good riddance."}


@router.delete("/")
async def delete_all_jobs(db: AsyncSession = Depends(get_db)):
    """Delete all jobs. No survivors."""
    count = await job_repository.clear_all(db)
    await db.commit()
    return {"message": f"Deleted {count} jobs. The market was garbage anyway."}
