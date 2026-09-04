# Gemini AI Key CRUD API 구현

users 테이블의 `ai_key` 컬럼을 활용하여 Gemini API Key 등록·조회·수정·삭제 기능을 구현합니다.
기존 아키텍처(Model → Schema → Service → Router) 흐름을 그대로 유지합니다.

## 아키텍처 분석

| 레이어 | 기존 패턴 |
|--------|-----------|
| Model | `User` 엔티티에 `ai_key: Mapped[str]` 컬럼 이미 존재 |
| Schema | `schemas/user.py` 내 Request/Response DTO 정의 |
| Service | `services/user.py` 내 `UserService` 클래스에 메서드 추가 |
| Router | `routers/user.py` 내 기존 라우터에 엔드포인트 추가 |

> [!IMPORTANT]
> **별도 파일 생성 없음**: `ai_key`는 `users` 테이블 컬럼이므로 새 모델 파일이 필요 없습니다.
> 기존 `UserService` + `user.py` 라우터에 메서드/엔드포인트만 추가합니다.

> [!NOTE]
> **인증 방식**: 현재 라우터에 JWT 의존성 주입(get_current_user)이 없습니다.
> 기존 패턴에 맞게 `user_id`를 URL 파라미터로 받는 방식으로 구현합니다.
> (추후 JWT 미들웨어 도입 시 쉽게 전환 가능한 구조)

## Proposed Changes

---

### 1. Schema — `schemas/user.py`

#### [MODIFY] [`user.py`](file:///Users/goorm_fullstack/Desktop/BE-Business/src/app/schemas/user.py)
추가할 DTO:
- `AiKeyRegisterRequest` — `ai_key: str` (등록/수정 Request)
- `AiKeyResponse` — 등록 결과 Response (`user_id`, `has_ai_key`, `message`)

---

### 2. Service — `services/user.py`

#### [MODIFY] [`user.py`](file:///Users/goorm_fullstack/Desktop/BE-Business/src/app/services/user.py)
`UserService` 클래스에 4개 메서드 추가:

| 메서드 | 설명 |
|--------|------|
| `register_ai_key(user_id, request)` | ai_key 등록 (이미 있으면 예외) |
| `get_ai_key(user_id)` | ai_key 존재 여부 조회 (값 노출 X) |
| `update_ai_key(user_id, request)` | ai_key 수정 |
| `delete_ai_key(user_id)` | ai_key 삭제 (NULL 처리) |

---

### 3. Router — `routers/user.py`

#### [MODIFY] [`user.py`](file:///Users/goorm_fullstack/Desktop/BE-Business/src/app/routers/user.py)
기존 라우터에 엔드포인트 추가:

| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/users/{user_id}/ai-key` | AI Key 등록 |
| `GET` | `/users/{user_id}/ai-key` | AI Key 등록 여부 조회 |
| `PUT` | `/users/{user_id}/ai-key` | AI Key 수정 |
| `DELETE` | `/users/{user_id}/ai-key` | AI Key 삭제 |

## Verification Plan

### Manual Verification (Postman)
1. `POST /users/{user_id}/ai-key` — Key 등록
2. `GET /users/{user_id}/ai-key` — 등록 여부 확인
3. `PUT /users/{user_id}/ai-key` — Key 수정
4. `DELETE /users/{user_id}/ai-key` — Key 삭제 후 GET으로 확인
