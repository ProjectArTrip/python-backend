from abc import ABC, abstractmethod


class ImageStoragePort(ABC):
    @abstractmethod
    def upload(self, *, key: str, content: bytes, content_type: str) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def public_url(self, key: str) -> str:
        pass
