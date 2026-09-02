# 1. 테이블 조인(Join)과 관계형 데이터베이스 핵심 개념

# 테이블 조인(Join)이란?
# 관계형 데이터베이스(Relational Database)에서 서로 연관된 여러 테이블의 데이터를 하나의 결과 집합으로 합쳐서 가져오는 기술
# 데이터 중복을 줄이기 위해 정보를 여러 테이블로 나누어 저장하는데(정규화),
# 서비스에서 데이터를 보여줄 때는 이 나누어진 정보들을 조인을 통해 다시 조립하여 조회합니다.

# 기본키(Primary Key)와 외래키(Foreign Key)
# - 기본키(Primary Key): 테이블에서 각 행(row)을 고유하게 식별, 유일하게 식별할 수 있는 고유한 값입니다.
#   중복될 수 없으며(Unique), 빈 값(NULL)을 가질 수 없습니다.
#   예: 사용자의 user_id (1, 2, 3, ...)

# 외래키(Foreign Key): 다른 테이블의 기본키를 참조하는 컬럼으로, 두 테이블 간의 관계를 정의합니다
# 다른 테이블의 기본키(PK)를 참조하는 컬럼으로, 두 테이블 간의 연결 고리 역할을 합니다.
# 예: 게시글 테이블(posts)에 있는 user_id (이 글을 어떤 사용자가 썼는지 나타냄)

# 테이블 간의 관계 (Relationship)
# [1:1 관계]
# 한 테이블의 행이 다른 테이블의 행과 정확히 하나씩만 연결되는 관계
# 예: 사용자(User)와 사용자 프로필(Profile)
# - User 테이블의 각 사용자는 Profile 테이블에 정확히 하나의 프로필을 가짐
# - Profile 테이블의 각 프로필은 User 테이블의 정확히 하나의 사용자에 속함

# [1:N 관계]
# 한 테이블의 행이 다른 테이블의 여러 행과 연결되는 관계
# 예: 사용자(User)와 게시글(Post)
# - User 테이블의 각 사용자는 Post 테이블에 여러 개의 게시글을 작성할 수 있음
# - Post 테이블의 각 게시글은 User 테이블의 정확히 하나의 사용자에 속함

# [N:N 관계]
# 두 테이블의 행이 서로 여러 행과 연결되는 관계
# 예: 학생(Student)과 강의(Course)
# - Student 테이블의 각 학생은 Course 테이블에서 여러 강의를 수강할 수 있음
# - Course 테이블의 각 강의는 Student 테이블에서 여러 학생이 수강할 수 있음
# - 이러한 관계를 표현하기 위해 중간 테이블(Enrollment)을 만들어 두 테이블을 연결함
# - RDB에서는 N:N 관계를 직접 맺을 수 없어, 중간에 연결 테이블을 두어 1:N - N:1 관계로 나누어 표현합니다.

# ERD (Entity Relationship Diagram) 차트란?
# ERD(엔티티 관계 다이어그램)는 데이터베이스의 구조를 시각적으로 표현한 것입니다.
# 엔티티(Entity): 데이터베이스에 저장되는 실제 개체(예: 사용자, 게시글)
# 관계(Relationship): 서로 다른 엔티티 간의 연결 관계(예: 1:N, N:N)
# 속성(Attribute): 각 엔티티가 가지는 특성(예: 사용자의 이름, 이메일)

from datetime import datetime
from typing import TYPE_CHECKING  # 추가

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from ..models.node import Node


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    ai_key: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # relationship의 Target 클래스는 문자열 "Node" 형태로 참조합니다.
    nodes: Mapped[list["Node"]] = relationship(back_populates="author")