## STEP 1 진행 완료 (2025-09-16)
- FastAPI 스캐폴딩 구성(app/main, config, routers/devices, models)
- 시뮬레이터 모드 환경변수 도입: SM_MODE=sim|hw (기본 sim)
- 엔드포인트:
  - GET /health
  - GET /api/devices
  - POST /api/devices/{id}/toggle
- 테스트: pytest + httpx(ASGITransport) + anyio 기반 비동기 테스트 2건 통과

### 해결한 오류들
- httpx 최신 버전에서 `AsyncClient(app=...)` 제거 → **ASGITransport**로 대체
- anyio가 trio 백엔드로도 파라미터라이즈 → **anyio_backend=asyncio**로 고정
- 일부 버전에서 `ASGITransport(..., lifespan="on")` 미지원 → **lifespan 인자 제거**

## STEP 2 진행 완료 (2025-09-16)
- 인메모리 이벤트 로그 도입(LogEntry: id, ts[UTC], device_id, action, note)
- 디바이스 토글 시 자동 로그 적재(append_log)
- GET /api/logs 추가 (쿼리: limit, device_id, action) — 최신순 정렬, limit 1~200 범위 처리
- 테스트: 토글 → 로그 생성 검증, device_id/action 필터 검증 통과

### 해결한 오류들
- PowerShell에서 `uvicorn` 명령 인식 안 됨 → 가상환경 내 실행으로 해결  
  - `python -m uvicorn app.main:app --reload` 또는 `.\.venv\Scripts\uvicorn.exe ...`
  - 필요 시 `python -m pip install -U "uvicorn[standard]" fastapi`

  ## STEP 3 진행 완료 (2025-09-16)
- 디바이스 업데이트 API 추가: PUT /api/devices/{id}
  - name/type/is_on 수정 가능
  - 수정 시 이벤트 로그(action="update") 자동 기록
- 테스트: 업데이트 성공/실패 케이스 + 로그 반영 확인 통과

### 해결한 오류들
- Action 리터럴에 `"update"` 누락 → Literal에 추가
- Pydantic v2 경고: `copy()`, `dict()` 대신 `model_copy()`, `model_dump()` 사용
- `/api/logs?action=update` 호출 시 422 오류 → Action 타입 일관성 유지로 해결