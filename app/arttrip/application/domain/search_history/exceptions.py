from arttrip.application.util.exception import DomainException, ErrorCode


class SearchHistoryError(DomainException):
    @classmethod
    def blank_keyword(cls) -> "SearchHistoryError":
        return cls(code="SEARCH_HISTORY_KEYWORD_BLANK", message="검색어를 입력하세요.")

    @classmethod
    def keyword_too_long(cls) -> "SearchHistoryError":
        return cls(
            code="SEARCH_HISTORY_KEYWORD_TOO_LONG", message="검색어가 너무 깁니다."
        )

    @classmethod
    def not_found(cls) -> "SearchHistoryError":
        return cls(
            code="SEARCH_HISTORY_NOT_FOUND",
            message="검색어를 찾을 수 없습니다.",
            error_code=ErrorCode.NOT_FOUND,
        )
