from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.idea import GenerateIdeaRequest, IdeaResponse
from ..services.idea import IdeaService

router = APIRouter(prefix="/ideas", tags=["Ideas"])


# 아이디어 비즈니스 로직을 위한 의존성 주입
def get_idea_service(db: Session = Depends(get_db)) -> IdeaService:
    return IdeaService(db=db)


# 1. 아이디어 생성 (LLM 연동 & Supabase DB 저장)
@router.post(
    "/generate",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="AI 기반 아이디어 생성",
    description="사용자의 ai_key와 최소 2개 이상의 노드를 결합하여 LLM을 통해 새로운 비즈니스 아이디어를 도출합니다.",
)
@router.post(
    "/create",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="아이디어 생성 (기존 경로 호환)",
)
@router.post(
    "",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="아이디어 생성 (기본 경로)",
)
async def generate_idea(
    request: GenerateIdeaRequest,
    idea_service: IdeaService = Depends(get_idea_service),
):
    return idea_service.generate_idea(request)



# 2. 아이디어 목록 조회
@router.get(
    "",
    response_model=list[IdeaResponse],
    summary="아이디어 목록 조회",
    description="아이디어 목록을 조회합니다. 사용자 ID(user_id) 필터링 및 페이징을 지원합니다.",
)
async def get_ideas(
    user_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
    idea_service: IdeaService = Depends(get_idea_service),
):
    return idea_service.get_ideas(user_id=user_id, skip=skip, limit=limit)


# 3. 아이디어 단일 상세 조회
@router.get(
    "/{id}",
    response_model=IdeaResponse,
    summary="아이디어 단일 조회",
    description="아이디어 ID를 통해 단일 아이디어와 연결된 노드 목록을 상세 조회합니다.",
)
async def get_idea(
    id: int,
    idea_service: IdeaService = Depends(get_idea_service),
):
    idea = idea_service.get_idea_by_id(id)
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Idea(id={id})를 찾을 수 없습니다.",
        )
    return idea


# 4. 아이디어 삭제
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="아이디어 삭제",
    description="아이디어를 삭제합니다. (연결된 조인 매핑 데이터도 함께 정리됩니다.)",
)
async def delete_idea(
    id: int,
    idea_service: IdeaService = Depends(get_idea_service),
):
    success = idea_service.delete_idea(id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Idea(id={id})를 찾을 수 없습니다.",
        )


# ============================================================
# [아이디어 수정 엔드포인트 - 구조 스켈레톤]
# 추후 아이디어 수정 기능이 필요할 경우 아래 엔드포인트를 활성화하여 구현합니다.
# ============================================================
# @router.put("/{id}", response_model=IdeaResponse, summary="아이디어 수정 (스켈레톤)")
# @router.patch("/{id}", response_model=IdeaResponse)
# async def update_idea(
#     id: int,
#     request: UpdateIdeaRequest,
#     idea_service: IdeaService = Depends(get_idea_service),
# ):
#     idea = idea_service.update_idea(id, request)
#     if not idea:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Idea(id={id})를 찾을 수 없습니다.",
#         )
#     return idea