from abc import ABC, abstractmethod
from typing import Collection

from arttrip.application.domain.keyword.keyword import Keyword
from arttrip.application.domain.keyword.keyword_type import KeywordType


class KeywordPort(ABC):
    @abstractmethod
    def list_all(self) -> list[Keyword]:
        pass

    @abstractmethod
    def find_by_ids(self, keyword_ids: Collection[int]) -> list[Keyword]:
        pass

    @abstractmethod
    def find_by_names(
        self, *, keyword_type: KeywordType, names: Collection[str]
    ) -> list[Keyword]:
        pass

    @abstractmethod
    def list_random_selected(self, *, user_id: int, limit: int) -> list[Keyword]:
        pass

    @abstractmethod
    def find_interested_user_ids(self, keyword_ids: Collection[int]) -> set[int]:
        pass
