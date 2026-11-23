from datetime import date
from typing import Sequence

from arttrip.application.domain.curation.curation_exhibit import CurationExhibit
from arttrip.application.domain.curation.exceptions import CurationError
from arttrip.application.domain.curation.refresh_cycle import RefreshCycle
from arttrip.application.domain.curation.sort_type import SortType


class Curation:
    def __init__(
        self,
        *,
        id_: int | None,
        title: str,
        active: bool,
        visible_from: date,
        visible_to: date,
        refresh_cycle: RefreshCycle,
        sort_type: SortType | None,
    ) -> None:
        self._id = id_
        self.title = title
        self.active = active
        self.visible_from = visible_from
        self.visible_to = visible_to
        self.refresh_cycle = refresh_cycle
        self.sort_type = sort_type
        self.exhibits: list[CurationExhibit] = []

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def is_visible(self) -> bool:
        return self.active

    @classmethod
    def create(
        cls,
        *,
        title: str,
        refresh_cycle: RefreshCycle,
        sort_type: SortType,
        visible_from: date,
        visible_to: date,
        active: bool,
        exhibit_ids: Sequence[int],
    ) -> "Curation":
        curation = cls(
            id_=None,
            title=title,
            active=active,
            visible_from=visible_from,
            visible_to=visible_to,
            refresh_cycle=refresh_cycle,
            sort_type=sort_type,
        )
        curation.revise(
            title=title,
            refresh_cycle=refresh_cycle,
            sort_type=sort_type,
            visible_from=visible_from,
            visible_to=visible_to,
            active=active,
        )
        curation.replace_exhibits(exhibit_ids)
        return curation

    def revise(
        self,
        *,
        title: str,
        refresh_cycle: RefreshCycle,
        sort_type: SortType,
        visible_from: date,
        visible_to: date,
        active: bool,
    ) -> None:
        normalized_title = title.strip()
        if not normalized_title:
            raise CurationError.title_required()
        if visible_from > visible_to:
            raise CurationError.invalid_period()
        self.title = normalized_title
        self.refresh_cycle = refresh_cycle
        self.sort_type = sort_type
        self.visible_from = visible_from
        self.visible_to = visible_to
        self.active = active

    def replace_exhibits(self, exhibit_ids: Sequence[int]) -> None:
        if not exhibit_ids:
            raise CurationError.exhibits_required()
        if len(set(exhibit_ids)) != len(exhibit_ids):
            raise CurationError.duplicate_exhibit()
        self.exhibits.clear()
        self.exhibits.extend(
            CurationExhibit(id_=None, exhibit_id=exhibit_id, display_order=order)
            for order, exhibit_id in enumerate(exhibit_ids)
        )
