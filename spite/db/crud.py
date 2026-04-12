from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from spite.db.models import Job, JobStatus


def create_job(db: Session, job_data: dict) -> tuple[Job, bool]:
    job = Job(**job_data)
    db.add(job)
    try:
        db.commit()
        db.refresh(job)
        return job, True
    except IntegrityError:
        db.rollback()
        existing = db.query(Job).filter(Job.url == job_data["url"]).first()
        return existing, False  # type: ignore


def get_jobs(
    db: Session,
    min_score: float | None = None,
    status: JobStatus | None = None,
    platform: str | None = None,
    limit: int = 50,
) -> list[Job]:
    query = db.query(Job)
    if min_score is not None:
        query = query.filter(Job.score >= min_score)
    if status is not None:
        query = query.filter(Job.status == status)
    if platform is not None:
        query = query.filter(Job.platform == platform)
    return query.order_by(Job.score.desc().nulls_last()).limit(limit).all()


def get_job_by_id(db: Session, job_id: int) -> Job | None:
    return db.query(Job).filter(Job.id == job_id).first()


def update_job_score(
    db: Session,
    job_id: int,
    score: float,
    summary: str,
    reasoning: str,
    red_flags: list[str],
    green_flags: list[str],
) -> Job | None:
    job = get_job_by_id(db, job_id)
    if not job:
        return None
    job.score = score
    job.score_summary = summary
    job.score_reasoning = reasoning
    job.red_flags = red_flags
    job.green_flags = green_flags
    job.status = JobStatus.SCORED
    db.commit()
    db.refresh(job)
    return job


def update_job_status(db: Session, job_id: int, status: JobStatus) -> Job | None:
    job = get_job_by_id(db, job_id)
    if not job:
        return None
    job.status = status
    db.commit()
    db.refresh(job)
    return job
