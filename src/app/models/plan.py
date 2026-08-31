from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)

    # 사업 계획서 상태 - ex) 임시저장, 발행 등
    status: Mapped[str] = mapped_column()

    # 사업 계획서 - 사업 분야 => 사업 분야와 문제인식 or 사업 분야와 솔루션 or 사업 분야와 스케일 업 or 사업 분야와 팀 빌딩
    # => 추후에 사업의 확장성을 위해 문제인식 / 해결방안 / 확장전략 / 팀빌딩 DB 테이블을 분리하여 관리할 필요성이 있음
    theme: Mapped[str] = mapped_column(String(100)) 

    # 사업계획서 문서 제목
    title: Mapped[str] = mapped_column(String(255)) 

    # 문제 인식 => TEXT가 길어지니까 혹시 str 타입이 아닐 수도 있으니 2차 검증이 필요
    problem: Mapped[str] = mapped_column()

    # 해결 방안 => TEXT가 길어지니까 혹시 str 타입이 아닐 수도 있으니 2차 검증이 필요
    solution: Mapped[str] = mapped_column()

    # 사업 확장 전략 => TEXT가 길어지니까 혹시 str 타입이 아닐 수도 있으니 2차 검증이 필요
    scale_up: Mapped[str] = mapped_column()

    # 팀 빌딩 => TEXT가 길어지니까 혹시 str 타입이 아닐 수도 있으니 2차 검증이 필요
    team_building: Mapped[str] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[str] = mapped_column()





