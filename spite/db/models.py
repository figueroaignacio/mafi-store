from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Text, Float, Integer, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from spite.db.engine import Base


class JobStatus(PyEnum):
    NEW = "new"
    SCORED = "scored"
    APPLIED = "applied"
    REJECTED = "rejected"
    IGNORED = "ignored"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    company: Mapped[str] = mapped_column(String(256), nullable=False)
    location: Mapped[str | None] = mapped_column(String(256), nullable=True)
    salary: Mapped[str | None] = mapped_column(String(128), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        default=JobStatus.NEW,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("url", name="uq_jobs_url"),
    )

    def __repr__(self) -> str:
        return f"<Job {self.id}: {self.title} @ {self.company} [{self.status.value}]>"
