from abc import ABC, abstractmethod
from typing import Sequence

from arttrip.application.port.input.exhibit.commands import (
    CreateExhibitCommand,
    DeleteArtistExhibitCommand,
    ExhibitImportRow,
    RegisterArtistExhibitCommand,
    UpdateArtistExhibitCommand,
    UpdateExhibitCommand,
)
from arttrip.application.port.input.exhibit.queries import (
    GetExhibitQuery,
    ListArtistExhibitsQuery,
    ListExhibitsQuery,
    ListRecentExhibitsQuery,
    SearchExhibitsQuery,
)
from arttrip.application.port.input.exhibit.results import (
    ExhibitDetail,
    ExhibitImportGuide,
    ExhibitImportPreview,
    ExhibitImportResult,
    ExhibitPage,
    ExhibitSearchItem,
    ExhibitSummary,
    ManagedExhibit,
)
from arttrip.application.port.input.pagination import OffsetPage
from arttrip.application.port.output.exhibit_source_port import SourcedExhibitPage


class GetExhibitUseCase(ABC):
    @abstractmethod
    def get_exhibit(self, query: GetExhibitQuery) -> ExhibitDetail:
        pass


class ListExhibitsUseCase(ABC):
    @abstractmethod
    def list_exhibits(self, query: ListExhibitsQuery) -> ExhibitPage:
        pass


class ListRecentExhibitsUseCase(ABC):
    @abstractmethod
    def list_recent_exhibits(
        self, query: ListRecentExhibitsQuery
    ) -> tuple[ExhibitSummary, ...]:
        pass


class SearchExhibitsUseCase(ABC):
    @abstractmethod
    def search_exhibits(
        self, query: SearchExhibitsQuery
    ) -> OffsetPage[ExhibitSearchItem]:
        pass


class GetManagedExhibitUseCase(ABC):
    @abstractmethod
    def get_managed_exhibit(self, exhibit_id: int) -> ManagedExhibit:
        pass


class UpdateExhibitUseCase(ABC):
    @abstractmethod
    def update_exhibit(self, command: UpdateExhibitCommand) -> None:
        pass


class DeleteExhibitUseCase(ABC):
    @abstractmethod
    def delete_exhibit(self, exhibit_id: int) -> None:
        pass


class CreateExhibitUseCase(ABC):
    @abstractmethod
    def create_exhibit(self, command: CreateExhibitCommand) -> int:
        pass


class GetExhibitImportGuideUseCase(ABC):
    @abstractmethod
    def get_exhibit_import_guide(self) -> ExhibitImportGuide:
        pass


class PreviewExhibitImportUseCase(ABC):
    @abstractmethod
    def preview_exhibit_import(
        self, rows: Sequence[ExhibitImportRow]
    ) -> ExhibitImportPreview:
        pass


class ImportExhibitsUseCase(ABC):
    @abstractmethod
    def import_exhibits(self, rows: Sequence[ExhibitImportRow]) -> ExhibitImportResult:
        pass


class RegisterArtistExhibitUseCase(ABC):
    @abstractmethod
    def register_artist_exhibit(self, command: RegisterArtistExhibitCommand) -> int:
        pass


class ListArtistExhibitsUseCase(ABC):
    @abstractmethod
    def list_artist_exhibits(
        self, query: ListArtistExhibitsQuery
    ) -> OffsetPage[ExhibitSearchItem]:
        pass


class UpdateArtistExhibitUseCase(ABC):
    @abstractmethod
    def update_artist_exhibit(self, command: UpdateArtistExhibitCommand) -> None:
        pass


class DeleteArtistExhibitUseCase(ABC):
    @abstractmethod
    def delete_artist_exhibit(self, command: DeleteArtistExhibitCommand) -> None:
        pass


class FetchOpenDataExhibitsUseCase(ABC):
    @abstractmethod
    def fetch_open_data_exhibits(self, page_index: int) -> SourcedExhibitPage:
        pass
