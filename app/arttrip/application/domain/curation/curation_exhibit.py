class CurationExhibit:
    def __init__(self, *, id_: int | None, exhibit_id: int, display_order: int) -> None:
        self._id = id_
        self.exhibit_id = exhibit_id
        self.display_order = display_order

    @property
    def id(self) -> int | None:
        return self._id
