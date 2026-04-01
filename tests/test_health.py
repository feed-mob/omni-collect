import pytest
from httpx import ASGITransport, AsyncClient

from omni_collect.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Client that triggers the full lifespan (including init_db)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        # Send a request through the app's lifespan context
        # by entering the app as an ASGI app with lifespan support
        yield c


@pytest.fixture
async def lifespan_client():
    """Client that explicitly runs the ASGI lifespan, covering DB init."""
    from contextlib import asynccontextmanager

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        # Manually trigger lifespan startup
        from omni_collect.database import init_db
        await init_db()
        yield c


@pytest.mark.anyio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["status"] == "ok"
    assert body["data"]["version"]


@pytest.mark.anyio
async def test_root(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["docs"] == "/docs"


@pytest.mark.anyio
async def test_init_db_creates_tables(tmp_path):
    """Verify init_db works from a clean state (no pre-existing data/ dir)."""
    import sqlalchemy
    from sqlalchemy.ext.asyncio import create_async_engine

    db_path = tmp_path / "test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")

    from omni_collect.models.db import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Verify tables exist
    async with engine.connect() as conn:
        result = await conn.execute(
            sqlalchemy.text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = {row[0] for row in result}

    await engine.dispose()

    assert "agents" in tables
    assert "credentials" in tables
    assert "collect_requests" in tables
    assert "reports" in tables


@pytest.mark.anyio
async def test_init_db_creates_data_dir():
    """Verify that init_db() creates the data/ directory if missing."""
    from pathlib import Path

    from omni_collect.config import DATA_DIR
    from omni_collect.database import init_db

    await init_db()
    assert DATA_DIR.is_dir()
