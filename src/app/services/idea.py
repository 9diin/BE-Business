import json
import logging
import os
import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ..models.idea import Idea
from ..models.node import Node
from ..models.user import User
from ..schemas.idea import GenerateIdeaRequest

logger = logging.getLogger(__name__)


class IdeaService:
    def __init__(self, db: Session):
        self.db = db

    def _call_llm(self, ai_key: str, system_prompt: str, user_prompt: str) -> dict[str, str]:
        """
        Google Gemini REST API (gemini-3.5-flash)를 호출하여 구조화된 아이디어 JSON 데이터를 추출합니다.
        """

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={ai_key.strip()}"
            prompt_text = f"{system_prompt}\n\n[요청 내용]\n{user_prompt}"

            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [
                            {
                                "parts": [
                                    {"text": prompt_text}
                                ]
                            }
                        ],
                        "generationConfig": {
                            "responseMimeType": "application/json",
                            "temperature": 0.7,
                        },
                    },
                )

            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("error", {}).get("message", error_detail)
                except Exception:
                    pass
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Gemini API 호출 중 오류가 발생했습니다: {error_detail}",
                )

            res_data = response.json()
            candidates = res_data.get("candidates", [])
            if not candidates:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Gemini API 응답에서 후보(candidates)를 찾을 수 없습니다.",
                )

            content_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            # 마크다운 정제 (```json ... ``` 형태 제거)
            content_text = content_text.strip()
            if content_text.startswith("```json"):
                content_text = content_text[7:]
            if content_text.startswith("```"):
                content_text = content_text[3:]
            if content_text.endswith("```"):
                content_text = content_text[:-3]
            content_text = content_text.strip()

            parsed_content = json.loads(content_text)

            return {
                "title": parsed_content.get("title", "생성된 비즈니스 아이디어"),
                "opinion": parsed_content.get("opinion", "아이디어 상세 의견이 도출되었습니다."),
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Gemini API 아이디어 도출 중 오류 발생")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"아이디어 생성 처리 중 오류가 발생했습니다: {str(e)}",
            )

    def generate_idea(self, request: GenerateIdeaRequest) -> Idea:
        """
        아이디어 자동 생성 비즈니스 로직:
        1. USERS 테이블에서 user_id 조회 및 ai_key 존재 여부 검증 (없을 경우 .env의 GEMINI_API_KEY 활용)
        2. NODES 테이블에서 해당 유저가 작성한 노드 중 request.node_ids에 해당하는 노드들을 조회
        3. 최소 2개 이상의 노드가 존재하는지 검증 (테이블 조인 활용을 위한 전제 조건)
        4. Gemini API를 호출하여 새로운 아이디어(제목, 의견) 도출
        5. 도출된 아이디어와 연결된 노드들을 idea_nodes 매핑 테이블을 통해 연결 후 Supabase DB에 저장
        """
        # 1. 유저 검증
        user = self.db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User(id='{request.user_id}')가 존재하지 않습니다.",
            )

        # 2. Gemini API Key 선택 (유저 ai_key 우선, 없으면 .env의 GEMINI_API_KEY)
        api_key = user.ai_key.strip() if (user.ai_key and user.ai_key.strip()) else os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", "")).strip()

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="해당 사용자의 Gemini API Key(ai_key)가 등록되어 있지 않으며, 서버의 GEMINI_API_KEY 환경변수도 설정되지 않았습니다.",
            )

        # 3. 노드 조회 (작성자 일치 여부 및 최소 2개 이상 선택 검증)
        nodes = (
            self.db.query(Node)
            .filter(
                Node.id.in_(request.node_ids),
                Node.user_id == request.user_id,
            )
            .all()
        )

        if len(nodes) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"아이디어를 생성하기 위해서는 해당 사용자({request.user_id})가 작성한 노드가 "
                    f"최소 2개 이상 필요합니다. (선택된 유효 노드 수: {len(nodes)}개)"
                ),
            )

        # 4. Gemini LLM 프롬프트 구성
        node_details = "\n".join(
            [
                f"- [노드 ID: {node.id}] [카테고리: {node.category}] 제목: {node.title} / 설명: {node.description}"
                for node in nodes
            ]
        )

        system_prompt = (
            "당신은 대한민국 대표 스타트업 비즈니스 모델 및 혁신 아이디어 전문 기획자입니다.\n"
            "사용자가 제공한 여러 개의 비즈니스 노드(아이디어 조각)들을 창의적이고 유기적으로 융합하여 "
            "새로운 비즈니스 아이디어의 제목(title)과 상세 분석 의견(opinion)을 도출해야 합니다.\n"
            "반드시 아래 JSON 포맷으로만 응답하세요. 다른 설명이나 마크다운 백틱(```json) 없이 순수 JSON 문자열만 출력하세요.\n"
            '{"title": "새로운 비즈니스 아이디어 제목", "opinion": "노드들의 결합 근거, 시장 기회, 구체적인 솔루션 및 기획 의견"}'
        )

        user_prompt = (
            f"다음은 사용자가 작성한 {len(nodes)}개의 비즈니스 노드 목록입니다:\n\n"
            f"{node_details}\n\n"
            "위 노드들의 강점과 아이디어를 융합하여 혁신적인 비즈니스 아이디어(title)와 구체적인 설명 및 의견(opinion)을 생성해주세요."
        )

        # 5. Gemini LLM 호출
        llm_result = self._call_llm(api_key, system_prompt, user_prompt)
        idea_title = llm_result["title"]
        idea_opinion = llm_result["opinion"]


        # 5. DB 엔티티 생성 및 연결된 노드들(N:M 관계) 매핑 후 Supabase DB에 저장
        new_idea = Idea(
            title=idea_title,
            opinion=idea_opinion,
            user_id=request.user_id,
        )
        new_idea.nodes = nodes

        self.db.add(new_idea)
        self.db.commit()
        self.db.refresh(new_idea)

        return new_idea


    def get_idea_by_id(self, idea_id: int) -> Idea | None:
        """
        ID로 단일 아이디어를 조회합니다. (연결된 노드 테이블 조인)
        """
        return (
            self.db.query(Idea)
            .options(joinedload(Idea.nodes))
            .filter(Idea.id == idea_id)
            .first()
        )

    def get_ideas(
        self,
        user_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Idea]:
        """
        아이디어 목록을 조회합니다. (사용자별 필터링 및 페이징 지원, 연결된 노드 조인)
        """
        query = self.db.query(Idea).options(joinedload(Idea.nodes))
        if user_id:
            query = query.filter(Idea.user_id == user_id)
        return query.order_by(Idea.created_at.desc()).offset(skip).limit(limit).all()

    def delete_idea(self, idea_id: int) -> bool:
        """
        아이디어를 삭제합니다. (연결된 idea_nodes 매핑도 CASCADE로 함께 정리됨)
        """
        idea = self.db.query(Idea).filter(Idea.id == idea_id).first()
        if not idea:
            return False

        self.db.delete(idea)
        self.db.commit()
        return True


    # ============================================================
    # [아이디어 수정 기능 - 구조 스켈레톤]
    # 추후 아이디어 수정 기능이 필요한 경우 아래 메서드를 활성화하여 사용할 수 있습니다.
    # ============================================================
    # def update_idea(self, idea_id: int, request: UpdateIdeaRequest) -> Idea | None:
    #     """
    #     아이디어 정보(제목, 의견 및 연결 노드)를 수정합니다. (스켈레톤)
    #     """
    #     idea = self.get_idea_by_id(idea_id)
    #     if not idea:
    #         return None
    #
    #     if request.title is not None:
    #         idea.title = request.title
    #     if request.opinion is not None:
    #         idea.opinion = request.opinion
    #     if request.node_ids is not None:
    #         # 새로운 노드 목록으로 조인 관계 갱신
    #         nodes = (
    #             self.db.query(Node)
    #             .filter(Node.id.in_(request.node_ids), Node.user_id == idea.user_id)
    #             .all()
    #         )
    #         idea.nodes = nodes
    #
    #     self.db.commit()
    #     self.db.refresh(idea)
    #     return idea
