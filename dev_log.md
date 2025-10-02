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

## STEP 10 진행 완료 (2025-09-24)
- devices 서비스 계층 분리 (`app/services/devices.py`)
  - CRUD/toggle 로직을 서비스로 이동
  - 라우터는 HTTP 처리만 담당
- append_log 호출, dict 직접 조작 등 중복 코드 제거
- 시드/시퀀스 관리도 서비스에 통합
- 기존 테스트 모두 재사용 가능 → pytest로 통합 확인

### 해결한 오류들
- 없음 (정상 동작)

## STEP 11 진행 완료 (2025-09-25)
- 주요 구현
  - 어댑터 인터페이스(`DeviceAdapter`) 정의
  - 하드웨어 모드 스텁(`HardwareStubAdapter`) 추가
  - 시뮬레이터 ↔ 하드웨어 모드 구조 분리 기초 완성
- 추가 개선
  - SM_MODE=hw 선택 시 하드웨어 스텁 사용 가능하도록 준비

### 해결한 오류들
- 없음 (스텁 레벨이라 단순 출력 확인만)

## STEP 12 진행 완료 (2025-09-30)
- 주요 구현
  - 시뮬레이터 모드 ↔ 하드웨어 모드 전환 구조(DI/Config 기반) 도입
  - `DeviceAdapter` 인터페이스 정의 및 `SimAdapter` / `HardwareStubAdapter` 구현
  - `app/deps.py`를 통해 라우터에서 모드별 어댑터 주입하도록 구성
  - `/health` 응답에 현재 모드(`sim`/`hw`) 추가
  - 앱 생성 시 및 어댑터 호출 시 시드 자동 주입 로직 보강 → 초기 404 방지
  - 테스트 안정화:
    - `test_hw_stub.py` → Device 반환 검증으로 변경
    - `test_mode_switch_di.py` → 연속 토글 기반으로 반전 여부 검증
  - `app/config.py`에서 `get_settings()` 기반 설정 관리, 하위호환용 `settings` 셔틀 추가

- 추가 개선
  - `print` 로그 캡처 의존 제거 → 토글 결과를 응답 JSON 기반으로 검증
  - `pytest` 환경에서 SM_MODE 전환 시 `importlib.reload`로 반영되도록 개선
  - `app/main.py` 시드 보증 및 로그 초기화 중복 방어

### 해결한 오류들
- `ImportError: cannot import name 'SimAdapter'` → 모듈 경로 및 `__init__.py` 수정
- `ModuleNotFoundError: No module named 'app.utils'` → 유틸 모듈 생성 및 정리
- `/health` KeyError('mode') → `/health` 응답에 `mode` 포함
- 초기 상태 404 (toggle, logs) → 앱 부팅 시/어댑터 호출 시 시드 강제 주입
- `AsyncClient(app=...)` 에러 → `ASGITransport` 사용으로 전환
- `capsys` 캡처 실패 → `print` 의존 제거, 응답 JSON으로 테스트
- `ImportError: cannot import name 'settings'` → `config.py`에 하위호환용 `settings` 추가

## STEP 13 진행 완료 (2025-09-30)
- 주요 구현
  - DB 코어: `app/db.py` (Base/engine/SessionLocal) 추가
  - ORM 모델: `DeviceORM`, `LogORM` 스켈레톤 정의
  - `app/models_orm.py` 임포트 시 자동 테이블 생성 보장 (`Base.metadata.create_all`)
  - 앱 기동 시에도 테이블 자동 생성 (중복 호출 무해)
  - DB 세션 의존성 주입 준비(`get_db` in `app/deps_db.py`)

- 테스트
  - `test_db_skeleton.py`: 테이블 존재 확인 및 CRUD 스모크 테스트
  - 중복 실행 시 UNIQUE 제약 충돌 → 테스트 이름에 UUID 접미사 추가로 해결
  - 전체 테스트 asyncio/trio 환경 모두 통과 확인

- 추가 개선
  - requirements.txt에 `SQLAlchemy>=2.0,<3.0` 의존성 추가
  - API는 여전히 인메모리 상태 유지, DB 전환은 STEP 14~15에서 순차 진행 예정

### 해결한 오류들
- `ModuleNotFoundError: No module named 'sqlalchemy'` → SQLAlchemy 설치
- `no such table: devices` → ORM 임포트 시 자동 테이블 생성 로직 추가
- `UNIQUE constraint failed: devices.name` → 테스트에서 UUID 접미사로 유니크 보장

## STEP 14 진행 완료 (2025-10-02)
- 주요 구현
  - `/api/devices` 목록/상세 **READ 경로를 SQLAlchemy 기반**으로 전환
  - **리포 계층** 추가: `app/repo/devices_db.py` (DB 조회/정렬/페이징 + 이름 중복 검사)
  - **삭제(DELETE)** 시 **DB에서도 동기 삭제** 추가 → READ 경로(DB 일원화)와 일치
  - **에러 문구 표준화**
    - 잘못된 정렬 키: `400` + `"Invalid order field"`
    - 이름 중복(대소문자 무시): `409` + `"name already exists"`
  - **CRUD 로그 보강**: create/update/delete 시 `append_log()` 호출

- 테스트
  - `test_db_list_detail_wire.py` 추가: DB 기반 목록/상세 스모크
  - `test_list_advanced.py`: 잘못된 `order` 케이스(400 + 문구) 통과
  - `test_validation.py`: 이름 중복 409 + 문구 검증 통과
  - `test_crud.py::test_delete_device_and_log`: 204 No Content + 삭제 로그 확인 통과

### 해결한 오류들
- `ModuleNotFoundError: No module named 'app.repo.devices_db'`  
  → `app/repo/` 패키지 및 `devices_db.py` 생성, 상대 임포트로 안정화.
- `assert 200 == 400` (잘못된 정렬 키에 200 반환)  
  → 목록 API에서 미허용 정렬 키일 때 `400` + `"Invalid order field"`로 고정.
- `assert 201 == 409` / `assert 200 == 409` (이름 중복 충돌 미처리)  
  → `name_exists()` 도입, POST/PUT에서 대소문자 무시 중복 시 `409` + `"name already exists"`.
- `assert 200 == 204` (DELETE 응답 코드 불일치)  
  → DELETE를 `204 No Content`로 통일(본문 미반환).
- 삭제 후에도 목록에 남음 (`assert all(d["id"] != did for d in items)`)  
  → READ는 DB, DELETE는 인메모리만 삭제하던 불일치 수정 → **DB 동기 삭제** 추가.
- CRUD 로그 누락으로 테스트 실패  
  → create/update/delete 모두 `append_log()` 호출 추가.

## STEP 15 (DB 연동 후 테스트 안정화)
- **DB/캐시 초기화 픽스처 충돌 해결**
  - 기존 `reset_state` (인메모리 초기화) + `_reset_db_and_state` (DB 초기화) 동시 autouse → 테스트 간 데이터 충돌 발생
  - 인메모리 시드 제거, DB 기반 SSOT 원칙 확립
- 최종 픽스처: `reset_db()` → `seed_devices()` → `refresh_cache_from_db()` → `reset_logs()`
  - Why: 모든 테스트 시작 시 DB/캐시/로그 상태를 깨끗하게 보장
  - What: DB drop/create 후 최소 3개 장치 시드, 캐시 동기화, 로그 초기화
  - How: autouse fixture `_reset_db_and_state`에서 일괄 처리
- **`@app.on_event("startup")` 정리**
  - 테스트와 중복되던 reset/seed 로직 제거 → `Base.metadata.create_all()`만 유지
- 테스트 결과: DB/캐시 불일치 오류, duplicate name 409 오류 등 해결됨

### 해결한 오류
- NameError: `SessionLocal` is not defined  
   → DB 모듈 구조 정리 및 `SessionLocal` 올바른 import 경로 지정
- Circular import (`engine` from partially initialized module)  
   → `db.py` 정리하여 Base/engine/SessionLocal 분리
- 테스트 간 상태 충돌 (duplicate name, 시드 불일치)  
   → 인메모리 초기화 제거, DB 단일 진실원칙(SSOT) 적용
- 409 Conflict (중복 이름) → 201 Created 기대 불일치 
   → 픽스처 격리로 해결, 테스트 통과 안정화