from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.exhibit.exhibit_hall import DEFAULT_COUNTRY_CODE


class Country:
    def __init__(
        self, *, id_: int | None, code: str, name: str, display_order: int
    ) -> None:
        self._id = id_
        self.code = code
        self.name = name
        self.display_order = display_order

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def is_domestic(self) -> bool:
        return self.code == DEFAULT_COUNTRY_CODE

    def ensure_overseas(self) -> None:
        if self.is_domestic:
            raise ExhibitError.domestic_mismatch()
