from arttrip.application.util.exception import DomainException, ErrorCode


class AuthError(DomainException):
    @classmethod
    def invalid_id_token(cls) -> "AuthError":
        return cls(
            code="AUTH_ID_TOKEN_INVALID",
            message="소셜 로그인 인증에 실패했습니다.",
            error_code=ErrorCode.UNAUTHENTICATED,
        )

    @classmethod
    def provider_unavailable(cls) -> "AuthError":
        return cls(
            code="AUTH_PROVIDER_UNAVAILABLE",
            message="소셜 로그인 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.",
            error_code=ErrorCode.UNAVAILABLE,
        )

    @classmethod
    def missing_access_token(cls) -> "AuthError":
        return cls(
            code="AUTH_ACCESS_TOKEN_MISSING",
            message="인증 토큰이 없습니다.",
            error_code=ErrorCode.UNAUTHENTICATED,
        )

    @classmethod
    def expired_access_token(cls) -> "AuthError":
        return cls(
            code="AUTH_ACCESS_TOKEN_EXPIRED",
            message="인증 토큰이 만료되었습니다.",
            error_code=ErrorCode.UNAUTHENTICATED,
        )

    @classmethod
    def invalid_access_token(cls) -> "AuthError":
        return cls(
            code="AUTH_ACCESS_TOKEN_INVALID",
            message="인증 토큰이 유효하지 않습니다.",
            error_code=ErrorCode.UNAUTHENTICATED,
        )

    @classmethod
    def invalid_refresh_token(cls) -> "AuthError":
        return cls(
            code="AUTH_REFRESH_TOKEN_INVALID",
            message="로그인이 만료되었습니다. 다시 로그인해 주세요.",
            error_code=ErrorCode.UNAUTHENTICATED,
        )

    @classmethod
    def permission_denied(cls) -> "AuthError":
        return cls(
            code="AUTH_PERMISSION_DENIED",
            message="권한이 없습니다.",
            error_code=ErrorCode.PERMISSION_DENIED,
        )

    @classmethod
    def unsupported_web_provider(cls) -> "AuthError":
        return cls(
            code="AUTH_WEB_PROVIDER_UNSUPPORTED",
            message="지원하지 않는 로그인 방식입니다.",
            error_code=ErrorCode.INVALID_ARGUMENT,
        )

    @classmethod
    def invalid_web_sign_in_request(cls) -> "AuthError":
        return cls(
            code="AUTH_WEB_SIGN_IN_REQUEST_INVALID",
            message="로그인 요청이 올바르지 않습니다. 처음부터 다시 시도해 주세요.",
            error_code=ErrorCode.INVALID_ARGUMENT,
        )

    @classmethod
    def web_sign_in_not_allowed(cls) -> "AuthError":
        return cls(
            code="AUTH_WEB_SIGN_IN_NOT_ALLOWED",
            message="관리자 계정만 로그인할 수 있습니다.",
            error_code=ErrorCode.PERMISSION_DENIED,
        )

    @classmethod
    def untrusted_origin(cls) -> "AuthError":
        return cls(
            code="AUTH_ORIGIN_NOT_ALLOWED",
            message="허용되지 않은 출처의 요청입니다.",
            error_code=ErrorCode.PERMISSION_DENIED,
        )
