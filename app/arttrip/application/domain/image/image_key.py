import secrets
from typing import Final

IMAGE_KEY_RANDOM_BYTES: Final = 32


def new_image_key(*, folder: str, extension: str) -> str:
    return f"{folder}/{secrets.token_hex(IMAGE_KEY_RANDOM_BYTES)}.{extension}"
