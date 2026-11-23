from arttrip.application.util.exception import DomainException


class KeywordError(DomainException):
    @classmethod
    def not_found(cls) -> "KeywordError":
        return cls(
            code="KEYWORD_NOT_FOUND",
            message="존재하지 않는 키워드가 포함되어 있습니다.",
        )
