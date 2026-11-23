from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Sequence

from arttrip.application.domain.exhibit.country import Country
from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.domain.exhibit.exhibit_factory import (
    new_exhibit,
    new_hall,
    revise_hall,
)
from arttrip.application.domain.exhibit.exhibit_hall import ExhibitHall
from arttrip.application.domain.exhibit.exhibit_status_policy import ExhibitStatusPolicy
from arttrip.application.domain.keyword.keyword import Keyword
from arttrip.application.domain.keyword.keyword_type import KeywordType
from arttrip.application.port.input.exhibit.commands import (
    CreateExhibitCommand,
    ExhibitImportRow,
)
from arttrip.application.port.input.exhibit.results import (
    ExhibitImportCandidate,
    ExhibitImportGuide,
    ExhibitImportIssue,
    ExhibitImportPreview,
    ExhibitImportResult,
)
from arttrip.application.port.input.exhibit.use_cases import (
    FetchOpenDataExhibitsUseCase,
    GetExhibitImportGuideUseCase,
    ImportExhibitsUseCase,
    PreviewExhibitImportUseCase,
)
from arttrip.application.port.output.exhibit_port import ExhibitKey
from arttrip.application.port.output.exhibit_source_port import (
    ExhibitSourcePort,
    SourcedExhibitPage,
)
from arttrip.application.port.output.unit_of_work import UnitOfWork
from arttrip.application.util.exception import DomainException
from arttrip.application.util.service_date import to_service_date


class GetExhibitImportGuideService(GetExhibitImportGuideUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def get_exhibit_import_guide(self) -> ExhibitImportGuide:
        with self._uow as uow:
            countries = uow.locations.list_countries()
            regions = uow.locations.list_regions()
            keywords = uow.keywords.list_all()
            return ExhibitImportGuide(
                country_names=tuple(country.name for country in countries),
                region_names=tuple(region.name for region in regions),
                genre_names=tuple(
                    keyword.name
                    for keyword in keywords
                    if keyword.keyword_type is KeywordType.GENRE
                ),
                style_names=tuple(
                    keyword.name
                    for keyword in keywords
                    if keyword.keyword_type is KeywordType.STYLE
                ),
            )


class PreviewExhibitImportService(PreviewExhibitImportUseCase):
    def __init__(self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy) -> None:
        self._uow = uow
        self._status_policy = status_policy

    def preview_exhibit_import(
        self, rows: Sequence[ExhibitImportRow]
    ) -> ExhibitImportPreview:
        today = to_service_date(datetime.now(UTC))
        with self._uow as uow:
            lookup = _load_import_lookup(uow, rows)
            return _plan_import(
                uow, rows, lookup, today=today, policy=self._status_policy
            )


class ImportExhibitsService(ImportExhibitsUseCase):
    def __init__(self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy) -> None:
        self._uow = uow
        self._status_policy = status_policy

    def import_exhibits(self, rows: Sequence[ExhibitImportRow]) -> ExhibitImportResult:
        today = to_service_date(datetime.now(UTC))
        with self._uow as uow:
            lookup = _load_import_lookup(uow, rows)
            plan = _plan_import(
                uow, rows, lookup, today=today, policy=self._status_policy
            )
            if plan.issues:
                return ExhibitImportResult(
                    exhibit_ids=(),
                    skipped_row_numbers=plan.duplicate_row_numbers,
                    issues=plan.issues,
                )
            exhibits = self._build_exhibits(uow, plan, lookup, today=today)
            uow.exhibits.add_all(exhibits)
            exhibit_ids = tuple(e.id for e in exhibits if e.id is not None)
        return ExhibitImportResult(
            exhibit_ids=exhibit_ids,
            skipped_row_numbers=plan.duplicate_row_numbers,
            issues=(),
        )

    def _build_exhibits(
        self,
        uow: UnitOfWork,
        plan: ExhibitImportPreview,
        lookup: _ImportLookup,
        *,
        today: date,
    ) -> list[Exhibit]:
        hall_names = {c.row.exhibit.hall_name.strip() for c in plan.candidates}
        halls: dict[str, ExhibitHall] = {}
        for found_hall in uow.exhibits.find_halls_by_names(hall_names):
            halls.setdefault(found_hall.name, found_hall)

        exhibits: list[Exhibit] = []
        for candidate in plan.candidates:
            command = candidate.row.exhibit
            country_code = lookup.countries[command.country_name].code
            hall_name = command.hall_name.strip()
            hall = halls.get(hall_name)
            if hall is None:
                hall = new_hall(command, country_code=country_code)
                halls[hall_name] = hall
            else:
                revise_hall(hall, command, country_code=country_code)
            exhibit = new_exhibit(
                command, hall=hall, today=today, policy=self._status_policy
            )
            keywords = {
                keyword.id: keyword
                for keyword in (
                    *(
                        lookup.genres[Keyword.normalize_name(n)]
                        for n in command.genre_names
                    ),
                    *(
                        lookup.styles[Keyword.normalize_name(n)]
                        for n in command.style_names
                    ),
                )
            }
            exhibit.replace_keywords(list(keywords.values()))
            exhibits.append(exhibit)
        return exhibits


class FetchOpenDataExhibitsService(FetchOpenDataExhibitsUseCase):
    def __init__(self, *, source: ExhibitSourcePort, page_size: int) -> None:
        self._source = source
        self._page_size = page_size

    def fetch_open_data_exhibits(self, page_index: int) -> SourcedExhibitPage:
        return self._source.fetch_page(page_no=page_index + 1, size=self._page_size)


def _plan_import(
    uow: UnitOfWork,
    rows: Sequence[ExhibitImportRow],
    lookup: _ImportLookup,
    *,
    today: date,
    policy: ExhibitStatusPolicy,
) -> ExhibitImportPreview:
    existing_keys = uow.exhibits.find_existing_keys(
        {_import_key(row.exhibit) for row in rows}
    )

    candidates: list[ExhibitImportCandidate] = []
    duplicate_row_numbers: list[int] = []
    issues: list[ExhibitImportIssue] = []
    seen_keys: set[ExhibitKey] = set()
    for row in rows:
        country = lookup.countries.get(row.exhibit.country_name)
        if country is None:
            issues.append(
                ExhibitImportIssue(
                    row.row_number,
                    "country_name",
                    f"등록되지 않은 국가입니다: {row.exhibit.country_name}",
                )
            )
            continue
        row_issues = _check_import_row(
            row,
            country,
            known_genres=set(lookup.genres),
            known_styles=set(lookup.styles),
            today=today,
            policy=policy,
        )
        if row_issues:
            issues.extend(row_issues)
            continue
        key = _import_key(row.exhibit)
        if key in existing_keys or key in seen_keys:
            duplicate_row_numbers.append(row.row_number)
            continue
        seen_keys.add(key)
        candidates.append(
            ExhibitImportCandidate(row=row, is_domestic=country.is_domestic)
        )
    return ExhibitImportPreview(
        candidates=tuple(candidates),
        duplicate_row_numbers=tuple(duplicate_row_numbers),
        issues=tuple(issues),
    )


def _check_import_row(
    row: ExhibitImportRow,
    country: Country,
    *,
    known_genres: set[str],
    known_styles: set[str],
    today: date,
    policy: ExhibitStatusPolicy,
) -> list[ExhibitImportIssue]:
    issues: list[ExhibitImportIssue] = []
    unknown_genres = sorted(
        name
        for name in row.exhibit.genre_names
        if Keyword.normalize_name(name) not in known_genres
    )
    if unknown_genres:
        issues.append(
            ExhibitImportIssue(
                row.row_number,
                "genre_names",
                f"등록되지 않은 장르입니다: {', '.join(unknown_genres)}",
            )
        )
    unknown_styles = sorted(
        name
        for name in row.exhibit.style_names
        if Keyword.normalize_name(name) not in known_styles
    )
    if unknown_styles:
        issues.append(
            ExhibitImportIssue(
                row.row_number,
                "style_names",
                f"등록되지 않은 전시 스타일입니다: {', '.join(unknown_styles)}",
            )
        )
    try:
        hall = new_hall(row.exhibit, country_code=country.code)
        new_exhibit(row.exhibit, hall=hall, today=today, policy=policy)
    except DomainException as error:
        issues.append(ExhibitImportIssue(row.row_number, None, str(error)))
    return issues


@dataclass(frozen=True)
class _ImportLookup:
    countries: dict[str, Country]
    genres: dict[str, Keyword]
    styles: dict[str, Keyword]


def _load_import_lookup(
    uow: UnitOfWork, rows: Sequence[ExhibitImportRow]
) -> _ImportLookup:
    return _ImportLookup(
        countries=uow.locations.map_countries_by_name(),
        genres=_keywords_by_name(
            uow, KeywordType.GENRE, {n for row in rows for n in row.exhibit.genre_names}
        ),
        styles=_keywords_by_name(
            uow, KeywordType.STYLE, {n for row in rows for n in row.exhibit.style_names}
        ),
    )


def _keywords_by_name(
    uow: UnitOfWork, keyword_type: KeywordType, names: set[str]
) -> dict[str, Keyword]:
    if not names:
        return {}
    found = uow.keywords.find_by_names(keyword_type=keyword_type, names=names)
    return {keyword.normalized_name: keyword for keyword in found}


def _import_key(command: CreateExhibitCommand) -> ExhibitKey:
    return (command.hall_name.strip(), command.title.strip(), command.start_date)
