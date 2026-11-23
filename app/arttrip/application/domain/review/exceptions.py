from arttrip.application.util.exception import DomainException, ErrorCode


class ReviewError(DomainException):
    @classmethod
    def invalid_content(cls) -> "ReviewError":
        return cls(
            code="REVIEW_CONTENT_INVALID",
            message="리뷰는 20~500자로 입력해 주세요.",
        )

    @classmethod
    def future_visit_date(cls) -> "ReviewError":
        return cls(
            code="REVIEW_VISIT_DATE_IN_FUTURE",
            message="방문일은 오늘 이전 날짜로 선택해 주세요.",
        )

    @classmethod
    def too_many_images(cls) -> "ReviewError":
        return cls(
            code="REVIEW_TOO_MANY_IMAGES",
            message="사진은 최대 4개까지 등록할 수 있습니다.",
        )

    @classmethod
    def image_not_found(cls) -> "ReviewError":
        return cls(
            code="REVIEW_IMAGE_NOT_FOUND",
            message="이 리뷰에 없는 사진입니다.",
        )

    @classmethod
    def banned_word_included(cls) -> "ReviewError":
        return cls(
            code="REVIEW_BANNED_WORD_INCLUDED",
            message="부적절한 표현이 있어 등록이 제한되었습니다. 수정 후 다시 시도해 주세요.",
        )

    @classmethod
    def already_written(cls) -> "ReviewError":
        return cls(
            code="REVIEW_ALREADY_WRITTEN",
            message="이 전시에는 이미 리뷰를 작성했습니다.",
            error_code=ErrorCode.ALREADY_EXISTS,
        )

    @classmethod
    def not_pending(cls) -> "ReviewError":
        return cls(
            code="REVIEW_NOT_PENDING",
            message="이미 심사가 끝난 리뷰입니다.",
            error_code=ErrorCode.ALREADY_EXISTS,
        )

    @classmethod
    def rejection_reason_required(cls) -> "ReviewError":
        return cls(
            code="REVIEW_REJECTION_REASON_REQUIRED",
            message="반려 사유는 1~200자로 입력해 주세요.",
        )

    @classmethod
    def not_found(cls) -> "ReviewError":
        return cls(
            code="REVIEW_NOT_FOUND",
            message="리뷰를 찾을 수 없습니다.",
            error_code=ErrorCode.NOT_FOUND,
        )
