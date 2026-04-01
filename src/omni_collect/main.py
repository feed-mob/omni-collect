from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from omni_collect.config import settings
from omni_collect.database import init_db
from omni_collect.models.schemas import ApiResponse, HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: include routers
# app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(collect_router, prefix="/api/v1", tags=["collect"])
# app.include_router(reports_router, prefix="/api/v1", tags=["reports"])


@app.get("/health")
async def health() -> ApiResponse[HealthResponse]:
    return ApiResponse(data=HealthResponse(version=settings.VERSION))


@app.get("/")
async def root() -> ApiResponse[dict]:
    return ApiResponse(
        data={
            "app": settings.APP_NAME,
            "version": settings.VERSION,
            "docs": "/docs",
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "omni_collect.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
