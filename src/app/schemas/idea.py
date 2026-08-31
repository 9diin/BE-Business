from pydantic import BaseModel

# idea(사업 아이템) 같은 경우에는 AI가 자동 생성해주기 때문에
# 수정할 필요가 없으므로 UpdateIdeaRequest는 현시점에 필요없다.

# 위 이유에 따라 Idea에 PSST 노드가 붙어 사업계획서 작성이 되기 때문에
# CreateIdeaRequest 네이밍은 변할 수 있다.
class CreateIdeaRequest(BaseModel):
    # id: str

    title: str

    opinion: str
