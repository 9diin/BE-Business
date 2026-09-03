from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from ..models.node import Node
    from ..models.user import User

# Idea와 Node 간의 다대다(N:M) 관계를 매핑하는 조인 테이블
idea_nodes = Table(
    "idea_nodes",
    Base.metadata,
    Column("idea_id", ForeignKey("ideas.id", ondelete="CASCADE"), primary_key=True),
    Column("node_id", ForeignKey("nodes.id", ondelete="CASCADE"), primary_key=True),
)


class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(255))

    opinion: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    author: Mapped["User"] = relationship(back_populates="ideas")

    # 최소 2개 이상의 노드를 결합하여 아이디어가 생성되므로 N:M 조인 관계로 노드들을 참조
    nodes: Mapped[list["Node"]] = relationship(
        "Node",
        secondary=idea_nodes,
        back_populates="ideas",
        lazy="selectin",
    )