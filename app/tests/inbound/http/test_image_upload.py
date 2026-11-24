from io import BytesIO

import pytest
from arttrip.inbound.http.image_upload import InvalidImageError, prepare_image
from PIL import Image

GENEROUS_PIXELS = 10_000_000
QUALITY = 85
CAMERA_MAKE_TAG = 0x010F
MAX_SIDE = 2048


def jpeg_bytes(size: tuple[int, int], exif: Image.Exif | None = None) -> bytes:
    buffer = BytesIO()
    image = Image.new("RGB", size, color="white")
    if exif is None:
        image.save(buffer, format="JPEG")
    else:
        image.save(buffer, format="JPEG", exif=exif)
    return buffer.getvalue()


class TestPrepareImage:
    def test_다시_저장한_이미지에는_EXIF가_남지_않는다(self) -> None:
        # given
        exif = Image.Exif()
        exif[CAMERA_MAKE_TAG] = "leaked-camera"
        original = jpeg_bytes((10, 10), exif=exif)

        # when
        prepared = prepare_image(
            original, max_pixels=GENEROUS_PIXELS, max_side=MAX_SIDE, quality=QUALITY
        )

        # then
        with Image.open(BytesIO(prepared.content)) as result:
            assert len(result.getexif()) == 0

    def test_화소_수가_상한을_넘으면_거절한다(self) -> None:
        # given
        max_pixels = 100
        one_pixel_over = jpeg_bytes((101, 1))

        # when, then
        with pytest.raises(InvalidImageError):
            prepare_image(
                one_pixel_over,
                max_pixels=max_pixels,
                max_side=MAX_SIDE,
                quality=QUALITY,
            )

    def test_이미지가_아닌_파일은_거절한다(self) -> None:
        # given
        not_image = b"<?php echo 'not an image'; ?>"

        # when, then
        with pytest.raises(InvalidImageError):
            prepare_image(
                not_image,
                max_pixels=GENEROUS_PIXELS,
                max_side=MAX_SIDE,
                quality=QUALITY,
            )
