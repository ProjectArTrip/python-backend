from arttrip.application.domain.keyword.keyword_type import KeywordType


class Keyword:
    def __init__(
        self, *, id_: int | None, name: str, keyword_type: KeywordType
    ) -> None:
        self._id = id_
        self.name = name
        self.keyword_type = keyword_type

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def normalized_name(self) -> str:
        return Keyword.normalize_name(self.name)

    @staticmethod
    def normalize_name(name: str) -> str:
        return "".join(name.split())
