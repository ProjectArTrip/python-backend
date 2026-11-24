from dataclasses import dataclass
from io import BytesIO
from typing import Final

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

ALLOWED_FORMATS: Final = frozenset({"JPEG", "MPO", "PNG", "WEBP"})
OUTPUT_FORMAT: Final = "JPEG"
OUTPUT_CONTENT_TYPE: Final = "image/jpeg"
OUTPUT_EXTENSION: Final = "jpg"
OUTPUT_MODE: Final = "RGB"


class InvalidImageError(Exception):
    pass


@dataclass(frozen=True)
class PreparedImage:
    content: bytes
    content_type: str
    extension: str


def prepare_image(
    content: bytes, *, max_pixels: int, max_side: int, quality: int
) -> PreparedImage:
    try:
        with Image.open(BytesIO(content)) as source:
            if source.format not in ALLOWED_FORMATS:
                raise InvalidImageError("JPEG, PNG, WebP 이미지만 올릴 수 있습니다.")
            width, height = source.size
            if width * height > max_pixels:
                raise InvalidImageError("이미지 해상도가 너무 큽니다.")
            source.thumbnail((max_side, max_side))
            upright = ImageOps.exif_transpose(source)
            cleaned = upright.convert(OUTPUT_MODE)
            output = BytesIO()
            cleaned.save(output, format=OUTPUT_FORMAT, quality=quality)
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError) as error:
        raise InvalidImageError("이미지 파일을 읽을 수 없습니다.") from error
    return PreparedImage(
        content=output.getvalue(),
        content_type=OUTPUT_CONTENT_TYPE,
        extension=OUTPUT_EXTENSION,
    )


def read_image_upload(
    file: UploadFile, *, max_bytes: int, max_pixels: int, max_side: int, quality: int
) -> PreparedImage:
    content = file.file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="이미지 파일이 너무 큽니다.")
    try:
        return prepare_image(
            content, max_pixels=max_pixels, max_side=max_side, quality=quality
        )
    except InvalidImageError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
