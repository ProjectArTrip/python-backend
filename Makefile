# 개발 중 반복하는 명령 묶음. 사용: make <이름>
.PHONY: fmt lint test check logs dev migrate revision reset-db

# 코드 정리 (자동 수정 포함)
fmt:
	poetry run ruff format app
	poetry run ruff check app --fix

# 정적 검사: 타입, 계층 의존 규칙
lint:
	poetry run mypy app
	poetry run lint-imports

# 도메인 테스트 (DB 없이 돈다)
test:
	poetry run pytest -q

# 코드를 고친 뒤 한 번에: 정리 → 검사 → 테스트. 하나라도 실패하면 거기서 멈춘다.
check: fmt lint test

# 개발 서버 로그 끝부분
logs:
	docker logs --tail 20 arttrip-backend

# 검사가 전부 통과하면 서버 로그까지 본다
dev: check logs

# models/ 를 고친 뒤 DB 에 반영
migrate:
	poetry run alembic upgrade head
	poetry run alembic check

VERSIONS := app/arttrip/outbound/persistence/alembic/versions
reset-db:
	rm -f $(VERSIONS)/*_0001_*.py $(VERSIONS)/*_0002_*.py
	poetry run alembic revision --autogenerate --rev-id 0001 -m "init"
	poetry run alembic upgrade 0001
	poetry run alembic revision --rev-id 0002 -m "keyword_data"
