# 필요한 라이브러리 설치 명령
# DB 연결 및 환경변수 로드를 위해 아래 패키지들이 설치되어 있어야 합니다.
# uv add fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv
# uv run uvicorn main:app --reload

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# .env 파일 로드
load_dotenv(override=True)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL이 .env 파일에 설정되지 않았습니다.")

# DB 엔진 생성
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # 끊어진 DB 연결 자동 감지 및 재연결
    pool_recycle=300,    # 5분 이상 비활성화된 커넥션 자동 재활성화 (Supabase 타임아웃 방지)
)

# DB 세션 생성기
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 엔티티들이 상속받을 공통 Base 클래스
class Base(DeclarativeBase):
    pass


# FastAPI 엔드포인트에서 사용할 DB 세션 의존성(Dependency)
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()