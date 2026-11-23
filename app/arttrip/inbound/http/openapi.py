from collections.abc import Callable
from typing import Any, Final

from arttrip.application.domain.auth.exceptions import AuthError
from arttrip.application.util.exception import DomainException
from arttrip.inbound.http.error import STATUS_BY_ERROR_CODE

ErrorFactory = Callable[[], DomainException]
Responses = dict[int | str, dict[str, Any]]

_DESCRIPTIONS: Final = {
    400: "요청을 처리할 수 없음",
    401: "인증 실패",
    403: "권한 없음",
    404: "대상을 찾을 수 없음",
    409: "현재 상태와 충돌",
    422: "요청 값 형식 오류",
    503: "외부 서비스 사용 불가",
}

AUTHENTICATION_ERRORS: Final[tuple[ErrorFactory, ...]] = (
    AuthError.missing_access_token,
    AuthError.expired_access_token,
    AuthError.invalid_access_token,
)
ADMIN_ERRORS: Final[tuple[ErrorFactory, ...]] = (
    *AUTHENTICATION_ERRORS,
    AuthError.permission_denied,
)


def _build_example(code: str, message: str) -> dict[str, Any]:
    return {"summary": code, "value": {"detail": message}}


def error_responses(*factories: ErrorFactory) -> Responses:
    examples_by_status: dict[int, dict[str, dict[str, Any]]] = {}
    for factory in factories:
        error = factory()
        status_code = STATUS_BY_ERROR_CODE[error.error_code]
        examples_by_status.setdefault(status_code, {})[error.code] = _build_example(
            error.code, str(error)
        )

    return {
        status_code: {
            "description": _DESCRIPTIONS.get(status_code, "오류"),
            "content": {"application/json": {"examples": examples}},
        }
        for status_code, examples in sorted(examples_by_status.items())
    }
