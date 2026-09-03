from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


# ==========================================
# Request DTOs
# ==========================================

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    id: str | None = None  # user_id 지정 (생략 시 UUID 또는 고유 ID 자동 생성)
    nickname: str | None = None
    phone: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserProfileUpdateRequest(BaseModel):
    nickname: str | None = None
    phone: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None


# ==========================================
# Response DTOs
# ==========================================

class UserProfileResponse(BaseModel):
    id: int
    user_id: str
    nickname: str | None = None
    phone: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    ai_key: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(BaseModel):
    id: str
    email: EmailStr
    ai_key: str | None = None
    created_at: datetime
    profile: UserProfileResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30분 (1800초)
    user: UserDetailResponse


class SignUpResponse(BaseModel):
    message: str
    user: UserDetailResponse
