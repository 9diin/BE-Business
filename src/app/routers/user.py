from fastapi import APIRouter  # noqa: I001
from ..schemas.user import SignUpRequest, SignInRequest

router = APIRouter()


# 회원가입
@router.post("/sign-up")
async def signup(request: SignUpRequest):
    # 비즈니스 로직
    return {"message": "회원가입을 완료하였습니다.", "request": request}


# 로그인
@router.get("/sign-in")
async def signin(request: SignInRequest):
    # 비즈니스 로직
    return {"message": "로그인을 완료하였습니다."}
