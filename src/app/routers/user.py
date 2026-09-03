from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.user import (
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
@router.post("/users/sign-up", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED)
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
@router.post("/login", response_model=TokenResponse)
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
