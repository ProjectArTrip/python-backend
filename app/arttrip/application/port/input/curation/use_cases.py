from abc import ABC, abstractmethod

from arttrip.application.port.input.curation.commands import (
    CreateCurationCommand,
    UpdateCurationCommand,
)
from arttrip.application.port.input.curation.queries import (
    GetCurationQuery,
    PickCurationQuery,
    SearchCurationsQuery,
)
from arttrip.application.port.input.curation.results import (
    CurationDetail,
    CurationSearchItem,
    CurationSummary,
    ManagedCuration,
)
from arttrip.application.port.input.pagination import OffsetPage


class GetCurationUseCase(ABC):
    @abstractmethod
    def get_curation(self, query: GetCurationQuery) -> CurationDetail:
        pass


class PickCurationUseCase(ABC):
    @abstractmethod
    def pick_curation(self, query: PickCurationQuery) -> CurationSummary:
        pass


class SearchCurationsUseCase(ABC):
    @abstractmethod
    def search_curations(
        self, query: SearchCurationsQuery
    ) -> OffsetPage[CurationSearchItem]:
        pass


class GetManagedCurationUseCase(ABC):
    @abstractmethod
    def get_managed_curation(self, curation_id: int) -> ManagedCuration:
        pass


class CreateCurationUseCase(ABC):
    @abstractmethod
    def create_curation(self, command: CreateCurationCommand) -> int:
        pass


class UpdateCurationUseCase(ABC):
    @abstractmethod
    def update_curation(self, command: UpdateCurationCommand) -> None:
        pass


class DeleteCurationUseCase(ABC):
    @abstractmethod
    def delete_curation(self, curation_id: int) -> None:
        pass
