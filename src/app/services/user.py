import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ..core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from ..models.user import User
from ..models.user_profile import UserProfile
from ..schemas.user import (
    SignInRequest,
    SignUpRequest,
    UserProfileUpdateRequest,
)


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def sign_up(self, request: SignUpRequest) -> User:
        """
        회원가입 비즈니스 로직:
        1. 이메일 중복 확인
        2. 비밀번호 암호화(bcrypt hashing)
        3. User 엔티티 및 UserProfile 엔티티 동시 생성 (1:1 관계)
        """
        # 이메일 중복 체크
        existing_email = self.db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 이메일 주소입니다.",
            )

        # user_id 결정 (제공되지 않은 경우 UUID 자동 생성)
        user_id = request.id if request.id else str(uuid.uuid4())

        # ID 중복 체크
        existing_id = self.db.query(User).filter(User.id == user_id).first()
        if existing_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 사용자 ID입니다.",
            )

        # 비밀번호 해싱
        hashed_password = hash_password(request.password)

        # User 생성
        new_user = User(
            id=user_id,
            email=request.email,
            password=hashed_password,
        )
        self.db.add(new_user)

        # UserProfile 기본 생성 (1:1 매핑)
        default_nickname = request.nickname or request.email.split("@")[0]
        new_profile = UserProfile(
            user_id=user_id,
            nickname=default_nickname,
            phone=request.phone,
            bio=request.bio,
            profile_image_url=request.profile_image_url,
        )
        self.db.add(new_profile)

        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def sign_in(self, request: SignInRequest) -> dict:
        """
        로그인 비즈니스 로직:
        1. 이메일로 사용자 조회 (UserProfile 조인)
        2. 비밀번호 해시 검증
        3. access_token(30분) 및 refresh_token 생성
        """
        user = (
            self.db.query(User)
            .options(joinedload(User.profile))
            .filter(User.email == request.email)
            .first()
        )
        if not user or not verify_password(request.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # JWT Payload 구성
        token_payload = {"sub": user.id, "email": user.email}
        access_token = create_access_token(data=token_payload)
        refresh_token = create_refresh_token(data={"sub": user.id})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,  # 30분
            "user": user,
        }

    def refresh_access_token(self, refresh_token_str: str) -> dict:
        """
        Refresh Token을 검증하여 새로운 access_token과 refresh_token을 재발급합니다.
        """
        try:
            payload = decode_token(refresh_token_str)
            if payload.get("token_type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="유효하지 않은 리프레시 토큰입니다.",
                )
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="토큰에 사용자 정보가 없습니다.",
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="만료되었거나 올바르지 않은 리프레시 토큰입니다.",
            )

        user = (
            self.db.query(User)
            .options(joinedload(User.profile))
            .filter(User.id == user_id)
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 토큰의 사용자를 찾을 수 없습니다.",
            )

        token_payload = {"sub": user.id, "email": user.email}
        new_access_token = create_access_token(data=token_payload)
        new_refresh_token = create_refresh_token(data={"sub": user.id})

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,
            "user": user,
        }

    def get_user_by_id(self, user_id: str) -> User:
        """
        user_id로 내 정보 및 마이페이지 프로필 조회 (User + UserProfile 조인)
        """
        user = (
            self.db.query(User)
            .options(joinedload(User.profile))
            .filter(User.id == user_id)
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User(id='{user_id}')를 찾을 수 없습니다.",
            )
        return user

    def update_profile(self, user_id: str, request: UserProfileUpdateRequest) -> User:
        """
        사용자 프로필 정보 수정
        """
        user = self.get_user_by_id(user_id)
        profile = user.profile

        if not profile:
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)

        if request.nickname is not None:
            profile.nickname = request.nickname
        if request.phone is not None:
            profile.phone = request.phone
        if request.bio is not None:
            profile.bio = request.bio
        if request.profile_image_url is not None:
            profile.profile_image_url = request.profile_image_url

        self.db.commit()
        self.db.refresh(user)
        return user
