from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.node import Node
from ..models.user import User
from ..schemas.node import CreateNodeRequest, UpdateNodeRequest


class NodeService:
    def __init__(self, db: Session):
        self.db = db

    def create_node(self, request: CreateNodeRequest) -> Node:
        """
        새로운 노드를 생성하여 DB에 저장합니다.
        """
        # 외래키(ForeignKey) 검증: user_id에 해당하는 사용자가 존재하는지 확인
        user = self.db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User(id='{request.user_id}')가 존재하지 않습니다. DB에 존재하는 유저의 ID를 입력해주세요.",
            )

        new_node = Node(
            title=request.title,
            description=request.description,
            category=request.category,
            user_id=request.user_id,
        )
        self.db.add(new_node)
        self.db.commit()
        self.db.refresh(new_node)
        return new_node


    def get_node_by_id(self, node_id: int) -> Node | None:
        """
        ID로 단일 노드를 조회합니다.
        """
        return self.db.query(Node).filter(Node.id == node_id).first()

    def get_nodes(self, user_id: str | None = None, skip: int = 0, limit: int = 100) -> list[Node]:
        """
        노드 목록을 조회합니다. (사용자별 필터링 및 페이징 지원)
        """
        query = self.db.query(Node)
        if user_id:
            query = query.filter(Node.user_id == user_id)
        return query.offset(skip).limit(limit).all()

    def update_node(self, node_id: int, request: UpdateNodeRequest) -> Node | None:
        """
        기존 노드 정보를 수정합니다.
        """
        node = self.get_node_by_id(node_id)
        
        if not node:
            return None

        if request.title is not None:
            node.title = request.title
        if request.description is not None:
            node.description = request.description
        if request.category is not None:
            node.category = request.category

        self.db.commit()
        self.db.refresh(node)
        return node

    def delete_node(self, node_id: int) -> bool:
        """
        노드를 삭제합니다.
        """
        node = self.get_node_by_id(node_id)
        if not node:
            return False

        self.db.delete(node)
        self.db.commit()
        return True



