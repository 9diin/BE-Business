from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.models.idea import Idea  # noqa: F401
from app.models.node import Node  # noqa: F401

# ⚠️ 이 문장이 들어가야 파이썬이 User 클래스를 메모리에 올리고 Base에 등록합니다.
from app.models.user import User  # noqa: F401
from app.routers.user import router as user_router

# 서버 시작 시 Supabase DB에 테이블 생성
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Base.metadata에 등록된 모델들을 기반으로 Supabase에 테이블 생성
#     Base.metadata.create_all(bind=engine)
#     yield

# main.py

@asynccontextmanager
async def lifespan(app: FastAPI):
    # async with -> with 로 변경
    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)
    yield


app = FastAPI(
    title="노드 연결 기반 사업계획서 자동 도출 플랫폼 - NODE-BIZ BACKEND",
    description="NODE-BIZ 백엔드 API 서비스 문서입니다.",
    version="1.0.0",
    docs_url="/api",
    lifespan=lifespan,
)


@app.get("/", tags=["Root"])
def main():
    return {"message": "Run FastAPI Server"}


app.include_router(user_router)