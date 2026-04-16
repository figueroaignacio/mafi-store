from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from spite.models.job import Job, JobStatus
from spite.repositories.base import BaseRepository
from spite.schemas.job import JobCreate, JobUpdate


class JobRepository(BaseRepository[Job, JobCreate, JobUpdate]):
    """Job-specific repository."""

    async def get_by_url(self, db: AsyncSession, url: str) -> Optional[Job]:
        result = await db.execute(select(Job).where(Job.url == url))
        return result.scalars().first()

    async def get_jobs_with_filters(
        self,
        db: AsyncSession,
        status: Optional[JobStatus] = None,
        platform: Optional[str] = None,
        limit: int = 50,
    ) -> List[Job]:
        query = select(Job)
        if status is not None:
            query = query.where(Job.status == status)
        if platform is not None:
            query = query.where(Job.platform == platform)

        query = query.order_by(Job.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def clear_all(self, db: AsyncSession) -> int:
        result = await db.execute(select(Job))
        count = len(result.scalars().all())
        await db.execute(delete(Job))
        return count


job_repository = JobRepository(Job)
