## STEP 1 진행 완료 (2025-09-15)
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

  ## STEP 3 진행 완료 (2025-09-17)
- 디바이스 업데이트 API 추가: PUT /api/devices/{id}
  - name/type/is_on 수정 가능
  - 수정 시 이벤트 로그(action="update") 자동 기록
- 테스트: 업데이트 성공/실패 케이스 + 로그 반영 확인 통과

### 해결한 오류들
- Action 리터럴에 `"update"` 누락 → Literal에 추가
- Pydantic v2 경고: `copy()`, `dict()` 대신 `model_copy()`, `model_dump()` 사용
- `/api/logs?action=update` 호출 시 422 오류 → Action 타입 일관성 유지로 해결

## STEP 4 진행 완료 (2025-09-18)
- 디바이스 CRUD 완성
  - POST /api/devices: 새 디바이스 생성 (sim 모드 전용)
  - DELETE /api/devices/{id}: 디바이스 삭제
- 이벤트 로그 확장: action="create", "delete" 기록
- 테스트: 생성/삭제 성공 및 로그 반영 검증 통과

### 해결한 오류들
- DeviceCreate 정의 누락 → app/models.py에 추가, routers/devices.py에서 import 보완
- 서버 기동 시 NameError 발생 → DeviceCreate 임포트 누락 수정으로 해결
- PowerShell REST 호출 시 JSON 전송 문제 → `-ContentType "application/json"` 지정으로 해결

## STEP 5 진행 완료 (2025-09-19)
- 디바이스 목록 API 고도화
  - 필터: type(light|plug|sensor), is_on(true|false)
  - 정렬: id|-id|name|-name|type|-type
  - 페이지네이션: page(기본 1), page_size(기본 20, 최대 50)
- GET /api/devices/{id} 상세 조회 추가
- 테스트: 필터/정렬/페이징/상세 조회 검증 통과

### 해결한 오류들
- update API에서 JSON Body 무시 → DeviceUpdate 모델 도입으로 해결
- DeviceUpdate 정의/임포트 누락으로 NameError 발생 → models.py 정의 및 devices.py import 보완

## STEP 6 진행 완료 (2025-09-20)
- 디바이스 상세 조회 API 안정화 (`GET /api/devices/{id}`)
  - 없는 ID → `404 {"detail":"Device not found"}` 표준화
  - Path 제약 추가: `device_id >= 1`
  - 테스트 케이스 추가: 성공/404 (anyio 기반 비동기)

### 해결한 오류들
- `fastapi` import 오타: `path` → `Path`
- 잘못된 가상환경으로 pytest 실행: langmate venv → smarthome venv로 교정
- anyio trio 백엔드 미설치: `ModuleNotFoundError: trio` → `pip install trio`로 해결
- 비동기 클라이언트 픽스처 부재: `async_client` 추가 (`tests/conftest.py`, httpx `ASGITransport`)
- PowerShell에서 404 응답 확인 시 예외: `-SkipHttpErrorCheck` 또는 try/catch로 본문 확인 가이드 제공

## STEP 7 진행 완료 (2025-09-21)
- 목록 API 고도화
  - `/api/devices` 응답을 **리스트** 형식으로 유지(기존 테스트 호환)
  - 고급 목록(`/api/devices/advanced`): `meta + items` 제공(페이지 정보 포함)
  - 정렬 필드 검증: 허용 외 필드 → **400 Invalid order field**
  - 필터 패턴 확장: `type`에 **plug** 추가
- 모델/시드
  - `Device.type`에 `plug` 허용
  - 시드 디바이스 3개 이상(plug 포함)
- 로그 아키텍처
  - 중앙 로그 서비스 도입: `app/services/logs.py`
  - `append_log(device_id, action, note=None)`로 단일화
  - `create/toggle/delete/update`에서 로그 기록 연동
  - `/api/logs`가 서비스 기반으로 조회
- 업데이트 API
  - `PUT /api/devices/{id}`에서 변경 사항 적용 및 `update` 로그 + note 포함
- 테스트
  - 기존 테스트 전부 통과(15/15)
  - 고급 목록 테스트는 `/api/devices/advanced`로 검증

### 해결한 오류들
- `type=plug` 미허용으로 인한 생성 실패 → 모델/쿼리 패턴 동기화
- 응답 스키마 불일치로 인한 KeyError → `/api/devices` 리스트 형식 복원
- 로그 스토어 분리로 증가 검증 실패 → 중앙 서비스로 통합
- 로그 스키마에 `note` 누락 → `append_log(..., note=None)` 추가

## STEP 8 진행 완료 (2025-09-21)
- 로그 필터링 API 고도화 (`GET /api/logs`)
  - `since`, `until` 파라미터 적용 시 ±ε(1e-3초) 보정 → 경계값 로그 누락 방지
  - `order=asc|desc` 옵션 정식 지원, 기본은 desc
  - 응답 포맷 일관화: 단일 로그여도 항상 리스트로 반환
  - 로그에 `note` 필드 기본 포함 (상세 변경 내역 기록 가능)

### 해결한 오류들
- `test_logs_since_until_and_order`: 경계 timestamp 누락 → ε 보정으로 해결
- `test_update_device_fields_and_log`: `append_log`가 `note` 인자 미지원 → 시그니처 확장
- `test_toggle_creates_log_and_list`: 로그 entry에 `note` 없음 → 기본 필드로 추가

## STEP 9 진행 완료 (2025-09-23)
- 디바이스 검증 강화
  - 이름 트리밍 후 길이 검증: 3~50자(공백 제거 후 판정)
  - 허용 타입 검증 유지: light|fan|outlet|sensor|plug
  - 이름 중복(대소문자 무시) 시 409 Conflict — 생성/수정 모두 적용
- 테스트 픽스처 정비
  - `tests/conftest.py`의 autouse 초기화에서 **시드 3개 보장**(Living Light, Desk Fan, Kitchen Outlet)
  - 필요 시 `_SEQ`(auto id)도 3으로 동기화

### 해결한 오류들
- `test_create_name_trim_and_length[trio]`
  - 원인: 이전 테스트에서 만든 이름과 겹쳐 409 발생
  - 조치: 테스트 격리를 위해 픽스처에서 상태 초기화 및 시드 재주입
- `test_filter_by_type_and_is_on_and_sort_paging`
  - 원인: 픽스처가 2개만 시드하여 테스트의 “최소 3개” 전제 충돌
  - 조치: 픽스처 시드를 3개로 상향 고정