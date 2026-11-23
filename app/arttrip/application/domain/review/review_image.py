class ReviewImage:
    def __init__(self, *, id_: int | None, image_key: str, display_order: int) -> None:
        self._id = id_
        self.image_key = image_key
        self.display_order = display_order

    @property
    def id(self) -> int | None:
        return self._id
