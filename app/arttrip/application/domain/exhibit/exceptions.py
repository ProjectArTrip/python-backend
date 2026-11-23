from arttrip.application.util.exception import DomainException, ErrorCode


class ExhibitError(DomainException):
    @classmethod
    def not_found(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_NOT_FOUND",
            message="전시를 찾을 수 없습니다.",
            error_code=ErrorCode.NOT_FOUND,
        )

    @classmethod
    def invalid_period(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_PERIOD_INVALID",
            message="조회 시작일과 종료일을 올바르게 입력하세요.",
        )

    @classmethod
    def unknown_country(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_COUNTRY_UNKNOWN",
            message="지원하지 않는 나라입니다.",
        )

    @classmethod
    def title_required(cls) -> "ExhibitError":
        return cls(code="EXHIBIT_TITLE_REQUIRED", message="전시 제목을 입력하세요.")

    @classmethod
    def invalid_schedule(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_SCHEDULE_INVALID",
            message="전시 시작일은 종료일보다 늦을 수 없습니다.",
        )

    @classmethod
    def hall_name_required(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_HALL_NAME_REQUIRED", message="전시관 이름을 입력하세요."
        )

    @classmethod
    def invalid_coordinates(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_HALL_COORDINATES_INVALID",
            message="위도와 경도를 올바르게 입력하세요.",
        )

    @classmethod
    def unknown_keyword(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_KEYWORD_UNKNOWN",
            message="등록되지 않은 장르 또는 스타일입니다.",
        )

    @classmethod
    def duplicate(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_DUPLICATE",
            message="같은 전시관에 같은 제목과 시작일의 전시가 이미 있습니다.",
            error_code=ErrorCode.ALREADY_EXISTS,
        )

    @classmethod
    def domestic_mismatch(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_COUNTRY_DOMESTIC_MISMATCH",
            message="해외 전시에는 한국을 고를 수 없습니다.",
        )

    @classmethod
    def region_requires_domestic(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_REGION_REQUIRES_DOMESTIC",
            message="지역 필터는 국내 전시에서만 쓸 수 있습니다.",
        )

    @classmethod
    def country_conflicts_with_domestic(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_COUNTRY_CONFLICTS_WITH_DOMESTIC",
            message="국내 전시 여부와 선택한 나라가 맞지 않습니다.",
        )

    @classmethod
    def unknown_region(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_REGION_UNKNOWN",
            message="지원하지 않는 지역입니다.",
        )

    @classmethod
    def invalid_cursor(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_CURSOR_INVALID",
            message="다음 쪽 정보가 올바르지 않습니다. 처음부터 다시 조회하세요.",
        )

    @classmethod
    def source_unavailable(cls) -> "ExhibitError":
        return cls(
            code="EXHIBIT_SOURCE_UNAVAILABLE",
            message="공공데이터에서 전시 정보를 가져올 수 없습니다. 잠시 후 다시 시도해 주세요.",
            error_code=ErrorCode.UNAVAILABLE,
        )
