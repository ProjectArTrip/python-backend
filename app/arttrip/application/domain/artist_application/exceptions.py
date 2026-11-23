from arttrip.application.util.exception import DomainException, ErrorCode


class ArtistApplicationError(DomainException):
    @classmethod
    def invalid_introduction(cls) -> "ArtistApplicationError":
        return cls(
            code="ARTIST_REQUEST_INTRODUCTION_INVALID",
            message="소개글은 1~1000자로 입력해 주세요.",
        )

    @classmethod
    def invalid_portfolio_url(cls) -> "ArtistApplicationError":
        return cls(
            code="ARTIST_REQUEST_PORTFOLIO_URL_INVALID",
            message="포트폴리오 주소는 https:// 로 시작하는 주소로 입력해 주세요.",
        )

    @classmethod
    def rejection_reason_required(cls) -> "ArtistApplicationError":
        return cls(
            code="ARTIST_REQUEST_REJECTION_REASON_REQUIRED",
            message="반려 사유는 1~500자로 입력해 주세요.",
        )

    @classmethod
    def already_reviewed(cls) -> "ArtistApplicationError":
        return cls(
            code="ARTIST_REQUEST_ALREADY_REVIEWED",
            message="이미 심사가 끝난 신청입니다.",
            error_code=ErrorCode.ALREADY_EXISTS,
        )

    @classmethod
    def already_pending(cls) -> "ArtistApplicationError":
        return cls(
            code="ARTIST_REQUEST_ALREADY_PENDING",
            message="이미 심사 중인 신청이 있습니다.",
            error_code=ErrorCode.ALREADY_EXISTS,
        )

    @classmethod
    def not_found(cls) -> "ArtistApplicationError":
        return cls(
            code="ARTIST_REQUEST_NOT_FOUND",
            message="아티스트 인증 신청 내역이 없습니다.",
            error_code=ErrorCode.NOT_FOUND,
        )
