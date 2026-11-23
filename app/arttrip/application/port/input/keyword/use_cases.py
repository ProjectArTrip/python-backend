from abc import ABC, abstractmethod

from arttrip.application.port.input.keyword.results import KeywordView


class ListKeywordsUseCase(ABC):
    @abstractmethod
    def list_keywords(self) -> list[KeywordView]:
        pass


class ListRecommendedKeywordsUseCase(ABC):
    @abstractmethod
    def list_recommended_keywords(self, user_id: int) -> list[KeywordView]:
        pass
