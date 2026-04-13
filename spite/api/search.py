import asyncio

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from spite.collectors.linkedin import LinkedInCollector
from spite.db import crud
from spite.db.engine import get_db
from spite.services.gemini import gemini_service

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    location: str = "Argentina"
    platform: str = "linkedin"
    hours: int = 24
    max_jobs: int = 50
    headless: bool = True
    score: bool = True


class SearchResult(BaseModel):
    found: int
    saved: int
    duplicates: int
    scored: int


def _run_search(
    query: str,
    location: str,
    hours: int,
    max_jobs: int,
    headless: bool,
    score: bool,
    db: Session,
) -> SearchResult:
    collector = LinkedInCollector(headless=headless)
    jobs = asyncio.run(
        collector.search(query, location, hours=hours, max_jobs=max_jobs)
    )

    found = len(jobs)
    saved = 0
    duplicates = 0
    scored = 0

    for job_data in jobs:
        job, created = crud.create_job(
            db,
            {
                "title": job_data.title,
                "company": job_data.company,
                "url": job_data.url,
                "platform": job_data.platform,
                "location": job_data.location,
                "salary": job_data.salary,
                "description": job_data.description,
            },
        )

        if created:
            saved += 1

            if score:
                description = asyncio.run(collector.get_description(job_data.url))

                # Truncar a 2000 caracteres para no gastar tokens de más
                if description:
                    description = description[:2000]
                    db_job = crud.get_job_by_id(db, job.id)
                    if db_job:
                        db_job.description = description
                        db.commit()

                result = gemini_service.score_job(
                    title=job_data.title,
                    company=job_data.company,
                    description=description or "",
                    location=job_data.location,
                    salary=job_data.salary,
                )

                crud.update_job_score(
                    db,
                    job.id,
                    score=result["score"],
                    summary=result.get("summary", ""),
                    reasoning=None,
                    red_flags=None,
                    green_flags=None,
                )
                scored += 1
        else:
            duplicates += 1

    return SearchResult(found=found, saved=saved, duplicates=duplicates, scored=scored)


@router.post("/", response_model=SearchResult)
def run_search(body: SearchRequest, db: Session = Depends(get_db)):
    """Scrape jobs and score them with Gemini."""
    return _run_search(
        query=body.query,
        location=body.location,
        hours=body.hours,
        max_jobs=body.max_jobs,
        headless=body.headless,
        score=body.score,
        db=db,
    )
