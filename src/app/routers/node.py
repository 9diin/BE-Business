from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.node import CreateNodeRequest, NodeResponse, UpdateNodeRequest
from ..services.node import NodeService

router = APIRouter(prefix="/nodes", tags=["Nodes"])


# 노드 비즈니스 로직을 위한 의존성 주입
def dependecy_node_service(db: Session = Depends(get_db)) -> NodeService:
    return NodeService(db=db)


# 노드 생성
@router.post("/create", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    request: CreateNodeRequest,
    node_service: NodeService = Depends(dependecy_node_service),
):
    return node_service.create_node(request)


# 노드 목록 조회
@router.get("", response_model=list[NodeResponse])
async def get_nodes(
    user_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
    node_service: NodeService = Depends(dependecy_node_service),
):
    return node_service.get_nodes(user_id=user_id, skip=skip, limit=limit)


# 노드 단일 조회
@router.get("/{id}", response_model=NodeResponse)
async def get_node(
    id: int,
    node_service: NodeService = Depends(dependecy_node_service),
):
    node = node_service.get_node_by_id(id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node(id={id})를 찾을 수 없습니다.",
        )
    return node


# 노드 수정
@router.put("/{id}", response_model=NodeResponse)
@router.patch("/{id}", response_model=NodeResponse)
@router.post("/{id}/update", response_model=NodeResponse)
async def update_node(
    id: int,
    request: UpdateNodeRequest,
    node_service: NodeService = Depends(dependecy_node_service),
):
    node = node_service.update_node(id, request)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node(id={id})를 찾을 수 없습니다.",
        )
    return node


# 노드 삭제
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    id: int,
    node_service: NodeService = Depends(dependecy_node_service),
):
    success = node_service.delete_node(id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node(id={id})를 찾을 수 없습니다.",
        )


