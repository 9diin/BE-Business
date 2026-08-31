from pydantic import BaseModel

# /plan/:id/update

class CreatePlanRequest(BaseModel):
    # id: int

    # status 같은 경우에는 사업계획서 생성된 시점에 상태 값이 바인딩 되는지 / 아닌지 체크 요망
    # status: str

    theme: str

    title: str

    # TEXT가 길어지니까 혹시 str 타입이 아닐 수도 있으니 2차 검증이 필요
    problem: str

    # TEXT가 길어지니까 혹시 str 타입이 아닐 수도 있으니 2차 검증이 필요
    solution: str

    # TEXT가 길어지니까 혹시 str 타입이 아닐 수도 있으니 2차 검증이 필요
    scale_up: str

    # TEXT가 길어지니까 혹시 str 타입이 아닐 수도 있으니 2차 검증이 필요
    team_building: str


class UpdatePlanRequest(BaseModel):
    id: int

    status: str
    
    theme: str | None
    
    title: str | None
    
    # TEXT가 길어지니까 혹시 str 타입이 아닐 수도 있으니 2차 검증이 필요
    problem: str | None

    # TEXT가 길어지니까 혹시 str 타입이 아닐 수도 있으니 2차 검증이 필요
    solution: str | None

    # TEXT가 길어지니까 혹시 str 타입이 아닐 수도 있으니 2차 검증이 필요
    scale_up: str | None

    # TEXT가 길어지니까 혹시 str 타입이 아닐 수도 있으니 2차 검증이 필요
    team_building: str | None