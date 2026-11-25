from arttrip.application.util.exception import DomainException, ErrorCode


class ExhibitReportError(DomainException):
    @classmethod
    def required_field_missing(cls, field: str) -> "ExhibitReportError":
        return cls(
            code="EXHIBIT_REPORT_REQUIRED_FIELD_MISSING",
            message=f"{field}을(를) 입력해 주세요.",
        )

    @classmethod
    def too_long(cls, field: str, max_length: int) -> "ExhibitReportError":
        return cls(
            code="EXHIBIT_REPORT_FIELD_TOO_LONG",
            message=f"{field}은(는) {max_length}자 이하로 입력해 주세요.",
        )

    @classmethod
    def invalid_schedule(cls) -> "ExhibitReportError":
        return cls(
            code="EXHIBIT_REPORT_INVALID_SCHEDULE",
            message="종료일은 시작일보다 빠를 수 없어요.",
        )

    @classmethod
    def invalid_source_url(cls) -> "ExhibitReportError":
        return cls(
            code="EXHIBIT_REPORT_SOURCE_URL_INVALID",
            message="공식 출처는 https:// 로 시작하는 주소로 입력해 주세요.",
        )

    @classmethod
    def rejection_reason_required(cls) -> "ExhibitReportError":
        return cls(
            code="EXHIBIT_REPORT_REJECTION_REASON_REQUIRED",
            message="반려 사유는 1~500자로 입력해 주세요.",
        )

    @classmethod
    def already_reviewed(cls) -> "ExhibitReportError":
        return cls(
            code="EXHIBIT_REPORT_ALREADY_REVIEWED",
            message="이미 검수가 끝난 제보입니다.",
            error_code=ErrorCode.ALREADY_EXISTS,
        )

    @classmethod
    def not_found(cls) -> "ExhibitReportError":
        return cls(
            code="EXHIBIT_REPORT_NOT_FOUND",
            message="제보 내역이 없습니다.",
            error_code=ErrorCode.NOT_FOUND,
        )
