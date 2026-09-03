from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from ..models.user import User


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # User와의 1:1 관계를 위한 외래키 (Unique 제약조건)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    nickname: Mapped[str] = mapped_column(String(100), nullable=True)

    phone: Mapped[str] = mapped_column(String(50), nullable=True)

    bio: Mapped[str] = mapped_column(String(500), nullable=True)

    profile_image_url: Mapped[str] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # 1:1 양방향 관계 설정 (User.profile과 1:1 매핑)
    user: Mapped["User"] = relationship(back_populates="profile")
