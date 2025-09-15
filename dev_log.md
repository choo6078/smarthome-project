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