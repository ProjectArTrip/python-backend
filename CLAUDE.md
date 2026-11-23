# ARTRIP backend

국내외 전시 정보를 찾고, 저장하고, 리뷰를 남기는 앱의 백엔드 API 서버다.

## 기능 범위

기능정의서 기준이다.

| 영역 | 기능 |
|---|---|
| 로그인 (LOGIN) | 소셜 로그인 (구글 등), 로그인 공통 동작 정책 |
| 온보딩 (ONB) | 닉네임 설정, 관심 키워드 (전시 장르, 스타일) 선택 저장 |
| 전시 (EX, MAIN) | 국내 전시 피드, 해외 전시 피드와 국가 필터, 지역별 전시, 조건 필터와 날짜 선택, 전시 상세와 상태 배지, 오늘 추천 전시, 개인화 추천 전시, 장르별 전시, 이번주 일정 전시, 큐레이션 전시 |
| 지도 (MAP) | 지도 기반 위치 표시, 지도 내 검색, 지도 내 전시 리스트 연동 |
| 검색 (SEARCH) | 전시 검색, 검색 기록 |
| 즐겨찾기 (HEART, LIKE) | 즐겨찾기 추가와 해제, 즐겨찾기 목록과 필터 |
| 리뷰 (REVIEW) | 리뷰 작성, 수정, 삭제, 전시별 리뷰 목록, 나의 리뷰 |
| 스탬프 (STAMP) | 리뷰 작성으로 스탬프 발급, 누적 수 기반 등급과 달성률 |
| 마이페이지 (MY) | 사용자 정보, 나의 취향 분석, 최근 본 전시, 공지사항, 푸시 알림 설정, 회원 탈퇴, 약관과 개인정보 처리방침 |
| 알림 (NOTI) | 알림 목록, 푸시 발송 |
| 전시 데이터 | 국내외 전시 데이터 수집, 마감 전시 데이터 정책 |

## 기술 스택

Python 3.14 / FastAPI / SQLAlchemy 2.0 / Alembic / PostgreSQL / Redis / Pydantic.
의존성은 Poetry, 가상환경은 `.venv` (`virtualenvs.in-project = true`).
외부 연동: OIDC 소셜 로그인, S3 이미지 저장, FCM 푸시, 공공데이터 전시 API.

## 아키텍처

헥사고날 (포트와 어댑터). 순수 DDD 가 아니다.

```
app/arttrip/
├── main.py                        조립 지점
├── common/                        설정. 다른 계층을 모른다
├── bootstrap/                     수명주기, 의존성 조립
├── application/
│   ├── domain/                    엔티티와 업무 규칙, 유스케이스 서비스
│   ├── port/input/                프라이머리 포트 (커맨드, 쿼리, 결과, 유스케이스)
│   └── port/output/               세컨더리 포트 (ABC)
├── inbound/http/                  프라이머리 어댑터. FastAPI
│   ├── routes/
│   └── schemas/                   Pydantic. 도메인과 분리
└── outbound/                      세컨더리 어댑터
    ├── persistence/
    │   ├── models/                Table 정의 + 매핑 함수
    │   ├── adapters/              포트 구현
    │   └── alembic/
    ├── oauth/
    ├── redis/
    ├── s3/
    ├── fcm/
    └── opendata/
```

### 파일을 어디에 둘지 판단하는 규칙

`from sqlalchemy import ...` 가 있으면 `outbound/persistence/`.
`from fastapi import ...` 가 있으면 `inbound/http/`.
둘 다 없으면 `application/`.

예외 없다. `pyproject.toml` 의 import-linter 계약이 강제한다.

### 계층별 책임

| 계층 | 하는 일 | 하지 않는 일 |
|---|---|---|
| `inbound/http` | 요청 파싱, 상태코드, JSON, 세션과 어댑터 조립 | 업무 규칙 |
| `application` 서비스 | 유스케이스 순서 (조회 → 도메인 호출 → 저장) | 업무 규칙 |
| `application/domain` 엔티티 | 업무 규칙, 불변식 | DB, HTTP, 프레임워크 |
| `outbound/` | 실제 SQL, 실제 HTTP 호출, 기술 예외를 도메인 예외로 변환 | 업무 규칙 |

업무 규칙을 유스케이스에 넣으면 빈약한 도메인 모델이 된다.

### 요청과 응답 이름

- 요청과 응답 필드는 `ApiModel` 의 camelCase 별칭 생성기로 이름을 정한다. 필드마다 `alias=` 를 손으로 붙이지 않는다
- 쿼리 파라미터는 엔드포인트마다 쿼리 파라미터 모델 하나로 받는다
- 파일이 섞인 요청은 폼 모델 하나로 받는다 (텍스트 필드와 파일을 같은 모델에 둔다)

## ORM

SQLAlchemy 2.0 imperative mapping. 도메인 클래스가 `sqlalchemy` 를 import 하지 않는다.

- `Table` 정의와 `map_*_table()` 함수는 같은 파일 (`models/<name>.py`)
- `models/all.py` 의 `map_tables()` 를 `main.py` 와 `alembic/env.py` 에서 각각 한 번 호출
- `where` 절은 `<name>_table.c.<column>` 으로 쓴다. 도메인 클래스 속성은 타입 검사기가 못 본다
- 애그리거트 자식은 `relationship(..., back_populates=...)` 로 연결한다. FK 를 유스케이스가 만지지 않는다
- 자격증명 칼럼은 `exclude_properties` 로 도메인에서 제외한다
- `env.py` 는 `models` 배럴을 import 해야 한다. 안 하면 빈 마이그레이션이 생성된다

## 보안

OWASP Top 10:2025 적용. 서버에서 deny-by-default 로 강제한다.

- 소셜 식별은 `(provider, sub)` 조합만 쓴다. `email` 은 식별자가 아니다 (OIDC Core 5.7)
- `role` 은 요청이 지정할 수 없다. `User.register()` 가 항상 `USER` 로 만든다
- 본인 리소스의 사용자 id 는 토큰에서만 꺼낸다. 요청 값으로 받지 않는다
- 리프레시 토큰은 `exclude_properties` 로 도메인에 적재하지 않는다
- 난수는 `secrets` 를 쓴다. `random` 은 쓰지 않는다
- 업무 제약은 도메인 모델이 먼저 막는다. DB 제약은 최종 방어선이다
- 비밀값은 환경변수와 `secrets/` 로만 주입한다. 레포에 커밋하지 않는다

## 테스트

`app/tests/domain/` 은 DB 없이 돈다. 이 성질을 깨지 않는다.
테스트는 최악 조건과 공격 엣지 케이스만 작성한다. 정상 흐름은 API 호출로 확인한다.
DB 를 띄우는 자동 테스트(Testcontainers 등)는 만들지 않는다.

## 명령

```bash
poetry run ruff format app && poetry run ruff check app --fix
poetry run lint-imports && poetry run mypy app && poetry run pytest -q

# models/ 를 고쳤을 때만
poetry run alembic revision --autogenerate -m "<message>"
poetry run alembic upgrade head && poetry run alembic check
```

로컬 DB 는 `docker compose up -d`. 초기화는 `docker compose down -v`.
