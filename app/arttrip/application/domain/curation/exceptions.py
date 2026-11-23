from arttrip.application.util.exception import DomainException, ErrorCode


class CurationError(DomainException):
    @classmethod
    def not_found(cls) -> "CurationError":
        return cls(
            code="CURATION_NOT_FOUND",
            message="큐레이션을 찾을 수 없습니다.",
            error_code=ErrorCode.NOT_FOUND,
        )

    @classmethod
    def title_required(cls) -> "CurationError":
        return cls(
            code="CURATION_TITLE_REQUIRED", message="큐레이션 제목을 입력하세요."
        )

    @classmethod
    def invalid_period(cls) -> "CurationError":
        return cls(
            code="CURATION_PERIOD_INVALID",
            message="노출 시작일은 종료일보다 늦을 수 없습니다.",
        )

    @classmethod
    def exhibits_required(cls) -> "CurationError":
        return cls(
            code="CURATION_EXHIBITS_REQUIRED",
            message="큐레이션에 담을 전시를 하나 이상 선택하세요.",
        )

    @classmethod
    def duplicate_exhibit(cls) -> "CurationError":
        return cls(
            code="CURATION_EXHIBIT_DUPLICATE",
            message="같은 전시를 두 번 담을 수 없습니다.",
        )

    @classmethod
    def unknown_exhibit(cls) -> "CurationError":
        return cls(
            code="CURATION_EXHIBIT_UNKNOWN",
            message="존재하지 않는 전시가 포함되어 있습니다.",
        )
