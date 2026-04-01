import importlib.util
import os
import shutil
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

from omni_collect.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
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
async def test_init_db_creates_data_dir_and_tables(tmp_path, monkeypatch):
    import sqlalchemy

    from omni_collect import database as db_module

    data_dir = tmp_path / "data"
    db_path = data_dir / "test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")

    monkeypatch.setattr(db_module, "DATA_DIR", data_dir)
    monkeypatch.setattr(db_module, "engine", engine)

    try:
        await db_module.init_db()

        assert data_dir.is_dir()

        async with engine.connect() as conn:
            result = await conn.execute(
                sqlalchemy.text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = {row[0] for row in result}
    finally:
        await engine.dispose()

    assert "agents" in tables
    assert "credentials" in tables
    assert "collect_requests" in tables
    assert "reports" in tables


def test_settings_load_repo_env_from_any_cwd(tmp_path):
    repo_root = tmp_path / "repo"
    package_dir = repo_root / "src" / "omni_collect"
    package_dir.mkdir(parents=True)

    source_config = Path(__file__).resolve().parents[1] / "src" / "omni_collect" / "config.py"
    shutil.copy(source_config, package_dir / "config.py")

    (repo_root / ".env").write_text(
        "\n".join(
            [
                "APP_NAME=FromEnv",
                "PORT=9999",
                "DATABASE_URL=sqlite+aiosqlite:///./data/test.db",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    spec = importlib.util.spec_from_file_location(
        "temp_omni_collect_config", package_dir / "config.py"
    )
    assert spec is not None and spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    previous_cwd = Path.cwd()

    try:
        os.chdir(elsewhere)
        spec.loader.exec_module(module)
    finally:
        os.chdir(previous_cwd)

    assert module.settings.APP_NAME == "FromEnv"
    assert module.settings.PORT == 9999
    assert module.make_url(module.settings.DATABASE_URL).database == str(
        repo_root / "data" / "test.db"
    )
