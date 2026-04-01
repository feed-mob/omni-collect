import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    public_key: Mapped[str] = mapped_column(Text)
    ip_address: Mapped[str] = mapped_column(String(45))
    registered_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


class Credential(Base):
    __tablename__ = "credentials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    platform: Mapped[str] = mapped_column(String(64), index=True)
    encrypted_data: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class CollectRequest(Base):
    __tablename__ = "collect_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("agents.agent_id"), index=True
    )
    topic: Mapped[str] = mapped_column(String(256))
    platforms: Mapped[dict | list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    completed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("agents.agent_id"), index=True
    )
    report_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    topic: Mapped[str] = mapped_column(String(256))
    report_md: Mapped[str] = mapped_column(Text, default="")
    raw_data_jsonl: Mapped[str] = mapped_column(Text, default="")
    generated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    synced_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
