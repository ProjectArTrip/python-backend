from datetime import UTC, datetime

from arttrip.application.domain.curation.curation import Curation
from arttrip.application.domain.curation.exceptions import CurationError
from arttrip.application.domain.curation.sort_type import SortType
from arttrip.application.domain.exhibit.exhibit_status_policy import ExhibitStatusPolicy
from arttrip.application.port.input.curation.commands import (
    CreateCurationCommand,
    UpdateCurationCommand,
)
from arttrip.application.port.input.curation.queries import SearchCurationsQuery
from arttrip.application.port.input.curation.results import (
    CurationSearchItem,
    ManagedCuration,
    ManagedCurationExhibit,
)
from arttrip.application.port.input.curation.use_cases import (
    CreateCurationUseCase,
    DeleteCurationUseCase,
    GetManagedCurationUseCase,
    SearchCurationsUseCase,
    UpdateCurationUseCase,
)
from arttrip.application.port.input.pagination import OffsetPage
from arttrip.application.port.output.unit_of_work import UnitOfWork
from arttrip.application.util.service_date import to_service_date


class SearchCurationsService(SearchCurationsUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def search_curations(
        self, query: SearchCurationsQuery
    ) -> OffsetPage[CurationSearchItem]:
        with self._uow as uow:
            total = uow.curations.count_search(
                keyword=query.keyword, active=query.active
            )
            rows = uow.curations.search_page(
                keyword=query.keyword,
                active=query.active,
                offset=query.page * query.size,
                limit=query.size,
            )
            items = tuple(
                CurationSearchItem(
                    curation_id=row.curation.id,
                    title=row.curation.title,
                    exhibit_count=row.exhibit_count,
                    created_at=to_service_date(row.created_at),
                    visible_from=row.curation.visible_from,
                    visible_to=row.curation.visible_to,
                    active=row.curation.active,
                )
                for row in rows
                if row.curation.id is not None
            )
            return OffsetPage(
                items=items, page=query.page, size=query.size, total_elements=total
            )


class GetManagedCurationService(GetManagedCurationUseCase):
    def __init__(self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy) -> None:
        self._uow = uow
        self._status_policy = status_policy

    def get_managed_curation(self, curation_id: int) -> ManagedCuration:
        today = to_service_date(datetime.now(UTC))
        with self._uow as uow:
            curation = uow.curations.find_by_id(curation_id)
            if curation is None:
                raise CurationError.not_found()
            exhibits = uow.curations.list_exhibits(curation_id)
            return ManagedCuration(
                curation_id=curation_id,
                title=curation.title,
                refresh_cycle=curation.refresh_cycle,
                sort_type=curation.sort_type or SortType.NONE,
                visible_from=curation.visible_from,
                visible_to=curation.visible_to,
                active=curation.active,
                exhibits=tuple(
                    ManagedCurationExhibit(
                        exhibit_id=exhibit.id,
                        title=exhibit.title,
                        poster_url=exhibit.poster_url,
                        status=exhibit.status_on(
                            today=today, policy=self._status_policy
                        ),
                        start_date=exhibit.start_date,
                        end_date=exhibit.end_date,
                        hall_name=exhibit.hall.name,
                    )
                    for exhibit in exhibits
                    if exhibit.id is not None
                ),
            )


class CreateCurationService(CreateCurationUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def create_curation(self, command: CreateCurationCommand) -> int:
        curation = Curation.create(
            title=command.title,
            refresh_cycle=command.refresh_cycle,
            sort_type=command.sort_type,
            visible_from=command.visible_from,
            visible_to=command.visible_to,
            active=command.active,
            exhibit_ids=command.exhibit_ids,
        )
        with self._uow as uow:
            existing_ids = uow.exhibits.find_existing_ids(command.exhibit_ids)
            if len(existing_ids) != len(command.exhibit_ids):
                raise CurationError.unknown_exhibit()
            uow.curations.add(curation)
            curation_id = curation.id
        if curation_id is None:
            raise RuntimeError("curation must be persisted before returning its id")
        return curation_id


class UpdateCurationService(UpdateCurationUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def update_curation(self, command: UpdateCurationCommand) -> None:
        with self._uow as uow:
            curation = uow.curations.find_by_id(command.curation_id)
            if curation is None:
                raise CurationError.not_found()
            curation.revise(
                title=command.title,
                refresh_cycle=command.refresh_cycle,
                sort_type=command.sort_type,
                visible_from=command.visible_from,
                visible_to=command.visible_to,
                active=command.active,
            )
            curation.replace_exhibits(command.exhibit_ids)
            existing_ids = uow.exhibits.find_existing_ids(command.exhibit_ids)
            if len(existing_ids) != len(command.exhibit_ids):
                raise CurationError.unknown_exhibit()


class DeleteCurationService(DeleteCurationUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def delete_curation(self, curation_id: int) -> None:
        with self._uow as uow:
            curation = uow.curations.find_by_id(curation_id)
            if curation is None:
                raise CurationError.not_found()
            uow.curations.remove(curation)
