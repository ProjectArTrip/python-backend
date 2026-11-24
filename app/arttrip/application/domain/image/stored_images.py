import logging
from collections.abc import Sequence
from dataclasses import dataclass

from arttrip.application.domain.image.exceptions import ImageError
from arttrip.application.domain.image.image_key import new_image_key
from arttrip.application.port.output.image_storage_port import ImageStoragePort

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UploadedImage:
    content: bytes
    content_type: str
    extension: str


def upload_all(
    storage: ImageStoragePort, images: Sequence[UploadedImage], *, folder: str
) -> list[str]:
    uploaded: list[str] = []
    try:
        for image in images:
            key = new_image_key(folder=folder, extension=image.extension)
            storage.upload(
                key=key, content=image.content, content_type=image.content_type
            )
            uploaded.append(key)
    except ImageError:
        delete_all_quietly(storage, uploaded)
        raise
    return uploaded


def delete_all_quietly(storage: ImageStoragePort, keys: Sequence[str]) -> None:
    for key in keys:
        delete_quietly(storage, key)


def delete_quietly(storage: ImageStoragePort, key: str) -> None:
    try:
        storage.delete(key)
    except ImageError:
        _logger.exception("stored image could not be deleted: %s", key)
