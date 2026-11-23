# ARTRIP backend

전시 정보 앱 백엔드.  Python 서버.

## 스택

Python 3.14, FastAPI, SQLAlchemy 2.0 (imperative mapping), Alembic, PostgreSQL, Redis, Firebase Admin(FCM).
의존성은 Poetry, 가상환경은 `.venv` (`virtualenvs.in-project = true`).

## 실행

```bash
cp .env.example .env
cp alembic.ini.example alembic.ini
docker compose up -d
poetry run alembic upgrade head
```

로컬 DB 초기화는 `docker compose down -v`.

## 검사

```bash
poetry run ruff format app && poetry run ruff check app --fix
poetry run lint-imports && poetry run mypy app && poetry run pytest -q
```

`lint-imports` 는 `5 kept, 0 broken` 이어야 한다.

## 아키텍처: 헥사고날 (포트와 어댑터)

```
app/arttrip/
├── main.py                  조립 지점
├── bootstrap/               lifespan, 의존성 조립
├── common/                  설정. 다른 계층을 모른다
├── application/
│   ├── domain/              엔티티와 업무 규칙, 유스케이스 서비스
│   └── port/
│       ├── input/           유스케이스 인터페이스, 커맨드, 결과
│       └── output/          세컨더리 포트 (ABC)
├── inbound/http/            프라이머리 어댑터. FastAPI 라우트와 Pydantic 스키마
└── outbound/                세컨더리 어댑터
    ├── persistence/         Table 정의, 매핑, 포트 구현, Alembic
    ├── fcm/                 FCM 발송
    ├── oauth/               소셜 로그인 검증
    ├── redis/
    ├── s3/                  이미지 저장
    └── token/               JWT 발급과 검증
```

파일 위치 규칙: `sqlalchemy` 를 import 하면 `outbound/persistence/`, `fastapi` 를 import 하면 `inbound/http/`, 둘 다 없으면 `application/`.
`pyproject.toml` 의 import-linter 계약이 강제한다.

| 계층 | 하는 일 | 하지 않는 일 |
|---|---|---|
| inbound/http | 요청 파싱, 상태 코드, 응답 변환, 입력 상한 검증 | 업무 규칙 |
| 유스케이스 서비스 | 순서 (조회, 도메인 호출, 저장) | 업무 규칙 |
| application/domain | 업무 규칙, 불변식 | DB, HTTP, 프레임워크 |
| outbound | SQL, 외부 호출, 기술 예외를 도메인 예외로 변환 | 업무 규칙 |

외부 발송(FCM 등)은 DB 트랜잭션 밖에서 한다. 커밋된 뒤에 보낸다.

## ORM

- 도메인 클래스는 `sqlalchemy` 를 import 하지 않는다.
- `Table` 정의와 `map_*_table()` 은 `outbound/persistence/models/<name>.py` 한 파일에 둔다.
- `models/all.py` 의 `map_tables()` 를 `main.py` 와 `alembic/env.py` 에서 각각 한 번 호출한다.
- `where` 절은 `<name>_table.c.<column>` 으로 쓴다.
- 애그리거트 자식은 `relationship(...)` 으로 연결한다. FK 를 유스케이스가 만지지 않는다.
- 자격증명 칼럼은 `exclude_properties` 로 도메인에서 뺀다.

## 보안 (OWASP Top 10)

- 서버에서 기본 거부로 강제한다.
- 소셜 식별은 `(provider, sub)` 조합만 쓴다. `email` 은 식별자가 아니다.
- `role` 은 요청으로 지정할 수 없다. 가입 시 항상 `USER` 다.
- 리프레시 토큰은 도메인에 적재하지 않는다.
- 토큰, 세션 값, 비밀번호, 개인정보는 로그와 print 에 원문으로 남기지 않는다. 기기 토큰은 SHA-256 해시로만 저장한다.
- 난수는 `secrets` 를 쓴다. `random` 은 쓰지 않는다.
- 업무 제약은 도메인이 먼저 막고, DB 제약은 최종 방어선이다.
- 외부 I/O 는 timeout 을 두고, 공유 클라이언트는 lifespan 에서 만들고 닫는다.

## 테스트

- 최악 조건과 공격 엣지 케이스만 작성한다 (경계값, 동시 요청, 재전송, 금지된 상태 전이, 소유권 침범, 주입, 과대 입력, 정보 노출).
- DB 를 띄우는 자동 테스트(Testcontainers 등)는 만들지 않는다. `app/tests/domain/` 은 DB 없이 돈다.

## 커밋하면 안 되는 것

`.env`, `.env.*` (`.env.example` 제외), `alembic.ini`, `secrets/`, Firebase 서비스 계정 키, APNs 키(`*.p8`, `*.p12`), `CLAUDE.md`.
`.gitignore` 가 막는다.
