from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.user import (
    AiKeyRegisterRequest,
    AiKeyResponse,
    RefreshTokenRequest,
    SignInRequest,
    SignUpRequest,
    SignUpResponse,
    TokenResponse,
    UserDetailResponse,
    UserProfileUpdateRequest,
)
from ..services.user import UserService

router = APIRouter(tags=["Users & Auth"])


# 유저 비즈니스 로직을 위한 의존성 주입
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db=db)


# 회원가입
@router.post("/sign-up", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED)
# @router.post("/users/sign-up", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignUpRequest,
    user_service: UserService = Depends(get_user_service),
):
    user = user_service.sign_up(request)
    return {
        "message": "회원가입이 성공적으로 완료되었습니다.",
        "user": user,
    }


# 로그인
@router.post("/sign-in", response_model=TokenResponse)
# @router.post("/login", response_model=TokenResponse)
async def signin(
    request: SignInRequest,
    user_service: UserService = Depends(get_user_service),
):
    return user_service.sign_in(request)


# 토큰 갱신 (30분 만료 시 refresh_token으로 access_token 재발급)
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    user_service: UserService = Depends(get_user_service),
):
    return user_service.refresh_access_token(request.refresh_token)


# user_id를 통한 회원 및 마이페이지 정보 조회 (User + UserProfile 1:1 조인)
@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_profile(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
):
    return user_service.get_user_by_id(user_id)


# 회원 프로필 정보 수정
@router.put("/users/{user_id}/profile", response_model=UserDetailResponse)
@router.patch("/users/{user_id}/profile", response_model=UserDetailResponse)
async def update_user_profile(
    user_id: str,
    request: UserProfileUpdateRequest,
    user_service: UserService = Depends(get_user_service),
):
    return user_service.update_profile(user_id, request)


# ==========================================
# Gemini AI Key CRUD 엔드포인트
# ==========================================

# [POST] AI Key 등록
@router.post(
    "/users/{user_id}/ai-key",
    response_model=AiKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gemini AI Key 등록",
    description="사용자의 Gemini AI Key를 등록합니다. 이미 등록된 Key가 있으면 409 에러를 반환합니다.",
)
async def register_ai_key(
    user_id: str,
    request: AiKeyRegisterRequest,
    user_service: UserService = Depends(get_user_service),
):
    return user_service.register_ai_key(user_id, request)


# [GET] AI Key 등록 여부 조회
@router.get(
    "/users/{user_id}/ai-key",
    response_model=AiKeyResponse,
    summary="Gemini AI Key 조회",
    description="사용자의 Gemini AI Key 등록 여부를 조회합니다. 실제 Key 값은 보안상 노출하지 않습니다.",
)
async def get_ai_key(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
):
    return user_service.get_ai_key(user_id)


# [PUT] AI Key 수정
@router.put(
    "/users/{user_id}/ai-key",
    response_model=AiKeyResponse,
    summary="Gemini AI Key 수정",
    description="등록된 Gemini AI Key를 수정합니다. 등록된 Key가 없는 경우 404 에러를 반환합니다.",
)
async def update_ai_key(
    user_id: str,
    request: AiKeyRegisterRequest,
    user_service: UserService = Depends(get_user_service),
):
    return user_service.update_ai_key(user_id, request)


# [DELETE] AI Key 삭제
@router.delete(
    "/users/{user_id}/ai-key",
    response_model=AiKeyResponse,
    summary="Gemini AI Key 삭제",
    description="등록된 Gemini AI Key를 삭제(NULL 초기화)합니다.",
)
async def delete_ai_key(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
):
    return user_service.delete_ai_key(user_id)
