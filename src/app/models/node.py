from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class Node(Base):
    # 실제 DB에 만들어질 테이블 이름
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(100))

    description: Mapped[str] = mapped_column(String(255))

    category: Mapped[str] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[str] = mapped_column()