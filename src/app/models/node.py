from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from ..models.idea import idea_nodes

if TYPE_CHECKING:
    from ..models.idea import Idea
    from ..models.user import User


class Node(Base):
    # 실제 DB에 만들어질 테이블 이름
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(100))

    description: Mapped[str] = mapped_column(String(255))

    category: Mapped[str] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    # Node와 User 간의 1:N 관계를 나타내는 속성
    author: Mapped["User"] = relationship(back_populates="nodes")

    # Node와 Idea 간의 N:M 다대다 관계를 나타내는 속성
    ideas: Mapped[list["Idea"]] = relationship(
        "Idea",
        secondary=idea_nodes,
        back_populates="nodes",
    )