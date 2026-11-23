from dataclasses import dataclass


@dataclass(frozen=True)
class ProfileImagePolicy:
    default_key: str

    def __post_init__(self) -> None:
        if not self.default_key.strip():
            raise ValueError("default_key must not be blank")

    def is_default(self, key: str) -> bool:
        return key == self.default_key
