from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from ..schemas.node import NodeResponse


# ==========================================
# Request DTOs
# ==========================================

class GenerateIdeaRequest(BaseModel):
    """
    아이디어 자동 생성 요청 DTO:
    - user_id: 아이디어를 생성하는 유저 ID (해당 유저의 ai_key 및 작성 노드 사용)
    - node_ids: 결합할 최소 2개 이상의 노드 ID 목록
    """
    user_id: str = Field(..., description="아이디어를 생성하는 사용자 ID")
    node_ids: list[int] = Field(
        ...,
        min_length=2,
        description="아이디어 추출에 활용할 최소 2개 이상의 노드 ID 리스트",
    )


# ============================================================
# [아이디어 수정 DTO - 구조 스켈레톤]
# 추후 아이디어 수정 기능 활성화 시 아래 Request DTO를 사용할 수 있습니다.
# ============================================================
# class UpdateIdeaRequest(BaseModel):
#     """
#     아이디어 수정 요청 DTO (스켈레톤)
#     """
#     title: str | None = Field(None, description="수정할 아이디어 제목")
#     opinion: str | None = Field(None, description="수정할 아이디어 의견/설명")
#     node_ids: list[int] | None = Field(None, description="수정할 연결 노드 ID 목록")


# ==========================================
# Response DTOs
# ==========================================

class IdeaResponse(BaseModel):
    """
    아이디어 응답 DTO:
    - Supabase DB에 저장된 아이디어 기본 정보 및 조인된 노드 목록 포함
    """
    id: int
    title: str
    opinion: str
    user_id: str
    created_at: datetime
    nodes: list[NodeResponse] = Field(default_factory=list, description="연결된 노드 상세 목록")

    model_config = ConfigDict(from_attributes=True)


class IdeaListResponse(BaseModel):
    """
    아이디어 목록 조회 응답 DTO
    """
    total: int
    ideas: list[IdeaResponse]

    model_config = ConfigDict(from_attributes=True)

