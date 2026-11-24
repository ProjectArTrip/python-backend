from arttrip.application.util.exception import DomainException, ErrorCode


class ImageError(DomainException):
    @classmethod
    def storage_unavailable(cls) -> "ImageError":
        return cls(
            code="IMAGE_STORAGE_UNAVAILABLE",
            message="이미지를 저장할 수 없습니다. 잠시 후 다시 시도해 주세요.",
            error_code=ErrorCode.UNAVAILABLE,
        )
