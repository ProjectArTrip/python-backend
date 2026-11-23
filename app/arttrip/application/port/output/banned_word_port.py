from abc import ABC, abstractmethod


class BannedWordPort(ABC):
    @abstractmethod
    def find_active_words(self) -> list[str]:
        pass
