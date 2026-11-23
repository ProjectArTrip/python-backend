from datetime import date
from typing import Sequence

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.exhibit.exhibit_hall import ExhibitHall
from arttrip.application.domain.exhibit.exhibit_status import ExhibitStatus
from arttrip.application.domain.exhibit.exhibit_status_policy import ExhibitStatusPolicy
from arttrip.application.domain.keyword.keyword import Keyword
from arttrip.application.domain.keyword.keyword_type import KeywordType


class Exhibit:
    def __init__(
        self,
        *,
        id_: int | None,
        hall: ExhibitHall,
        title: str | None,
        description: str | None,
        poster_url: str | None,
        ticket_url: str | None,
        status: ExhibitStatus,
        start_date: date | None,
        end_date: date | None,
        owner_id: int | None = None,
    ) -> None:
        self._id = id_
        self.hall = hall
        self.title = title
        self.description = description
        self.poster_url = poster_url
        self.ticket_url = ticket_url
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.keywords: list[Keyword] = []
        self.owner_id = owner_id

    @property
    def id(self) -> int | None:
        return self._id

    @classmethod
    def create(
        cls,
        *,
        hall: ExhibitHall,
        title: str,
        description: str | None,
        poster_url: str | None,
        ticket_url: str | None,
        start_date: date | None,
        end_date: date | None,
        today: date,
        policy: ExhibitStatusPolicy,
        owner_id: int | None = None,
    ) -> "Exhibit":
        exhibit = cls(
            id_=None,
            hall=hall,
            title=title,
            description=description,
            poster_url=poster_url,
            ticket_url=ticket_url,
            status=ExhibitStatus.ONGOING,
            start_date=start_date,
            end_date=end_date,
            owner_id=owner_id,
        )
        exhibit.revise(
            title=title,
            description=description,
            poster_url=poster_url,
            ticket_url=ticket_url,
            start_date=start_date,
            end_date=end_date,
        )
        exhibit.status = exhibit.status_on(today=today, policy=policy)
        return exhibit

    def status_on(self, *, today: date, policy: ExhibitStatusPolicy) -> ExhibitStatus:

        if self.start_date is not None and today < self.start_date:
            return ExhibitStatus.UPCOMING

        if self.end_date is None:
            return ExhibitStatus.ONGOING

        if today > self.end_date:
            return ExhibitStatus.FINISHED

        if self.end_date <= policy.ending_soon_until(today):
            return ExhibitStatus.ENDING_SOON

        return ExhibitStatus.ONGOING

    def revise(
        self,
        *,
        title: str,
        description: str | None,
        poster_url: str | None,
        ticket_url: str | None,
        start_date: date | None,
        end_date: date | None,
    ) -> None:
        if not title.strip():
            raise ExhibitError.title_required()
        if start_date is not None and end_date is not None and start_date > end_date:
            raise ExhibitError.invalid_schedule()
        self.title = title.strip()
        self.description = description
        self.poster_url = poster_url
        self.ticket_url = ticket_url
        self.start_date = start_date
        self.end_date = end_date

    def replace_keywords(self, keywords: Sequence[Keyword]) -> None:
        self.keywords = list(keywords)

    def keyword_names(self, keyword_type: KeywordType) -> tuple[str, ...]:
        return tuple(
            keyword.name
            for keyword in self.keywords
            if keyword.keyword_type is keyword_type
        )

    def ensure_owned_by(self, user_id: int) -> None:
        if self.owner_id is None or self.owner_id != user_id:
            raise ExhibitError.not_found()
