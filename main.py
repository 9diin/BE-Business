from fastapi import FastAPI

from app.routers.user import router as user_router

app = FastAPI(
    title="노드 연결 기반 사업계획서 자동 도출 플랫폼 - NODE-BIZ BACKEND",
    description="NODE-BIZ 백엔드 API 서비스 문서입니다.",
    version="1.0.0",
    docs_url="/api",
)

@app.get("/")
def main():
    return {"Run FastAPI Server"}

app.include_router(user_router)