from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ── Unified response ──────────────────────────────────────────────


class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "ok"
    data: T | None = None


# ── Health ─────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str


# ── Auth ───────────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    public_key: str


class RegisterResponse(BaseModel):
    agent_id: str
    registered_at: datetime


# ── Collect ────────────────────────────────────────────────────────


class CollectRequest(BaseModel):
    topic: str
    platforms: list[str] = Field(default_factory=list)
    options: dict | None = None


class CollectItem(BaseModel):
    """Standard JSONL item from any platform."""

    platform: str
    type: str  # post, repo, tweet, ...
    id: str
    title: str = ""
    content: str = ""
    author: str = ""
    url: str = ""
    likes: int = 0
    comments: int = 0
    timestamp: datetime | None = None


class PlatformResult(BaseModel):
    platform: str
    status: str  # ok / error
    count: int = 0
    data: list[CollectItem] = Field(default_factory=list)
    error: str | None = None


class CollectResponse(BaseModel):
    request_id: str
    results: list[PlatformResult]


# ── Reports ────────────────────────────────────────────────────────


class ReportSyncRequest(BaseModel):
    topic: str
    report_md: str
    raw_data_jsonl: str = ""
    generated_at: datetime | None = None


class ReportSyncResponse(BaseModel):
    report_id: str
    url: str


class ReportSummary(BaseModel):
    report_id: str
    topic: str
    generated_at: datetime | None
    url: str
