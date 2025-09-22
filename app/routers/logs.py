from fastapi import APIRouter, Query
from typing import Annotated, Literal
# 라우터는 서비스 레이어만 의존 -> 내부 저장 방식(메모리/DB) 변경에 둔감
from app.services.logs import list_logs as _list_logs

router = APIRouter(prefix="/api", tags=["logs"])

@router.get("/logs")
@router.get("/logs")
async def get_logs(
    # 액션 필터: 없으면 전체
    action: Annotated[Literal["create", "toggle", "delete", "update"] | None, Query()] = None,
    # 특정 디바이스만 보고 싶을 때
    device_id: Annotated[int | None, Query(ge=1)] = None,
    # 가져올 개수 제한 (UI에서 "최근 50건" 같은 뷰를 만들기 좋음)
    limit: Annotated[int | None, Query(ge=0)] = None,
    # 기간 필터: epoch seconds (float). 프론트에서 Date -> epoch 변환해서 넘기면 됨.
    since: Annotated[float | None, Query(description="epoch seconds (>= since)")] = None,
    until: Annotated[float | None, Query(description="epoch seconds (<= until)")] = None,
    # 정렬: asc(오래된→최신) | desc(최신→오래된). 기본 desc가 일반적인 타임라인 UX와 맞음.
    order: Annotated[Literal["asc", "desc"] | None, Query(pattern="^(asc|desc)$")] = "desc",
):
    # 서비스에 모든 필터/정렬 로직을 위임 (라우터는 파라미터 검증/문서화에 집중)
    return _list_logs(
        action=action,
        device_id=device_id,
        limit=limit,
        since=since,
        until=until,
        order=order or "desc",
    )