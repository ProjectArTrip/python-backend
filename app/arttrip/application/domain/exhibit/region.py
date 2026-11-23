class Region:
    def __init__(
        self,
        *,
        id_: int | None,
        name: str,
        image_url: str | None,
        display_order: int,
    ) -> None:
        self._id = id_
        self.name = name
        self.image_url = image_url
        self.display_order = display_order

    @property
    def id(self) -> int | None:
        return self._id
