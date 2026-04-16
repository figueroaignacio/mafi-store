from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    location: str = "Argentina"
    platform: str = "linkedin"
    hours: int = 24
    max_jobs: int = 50
    headless: bool = True
    analyze: bool = True


class SearchResult(BaseModel):
    found: int
    saved: int
    duplicates: int
    analyzed: int
