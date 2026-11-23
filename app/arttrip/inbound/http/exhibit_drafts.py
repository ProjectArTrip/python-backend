from collections.abc import Sequence
from typing import Final

from pydantic import ValidationError

from arttrip.application.port.input.exhibit.commands import ExhibitImportRow
from arttrip.application.port.input.exhibit.results import ExhibitImportIssue
from arttrip.application.port.output.exhibit_source_port import SourcedExhibit
from arttrip.inbound.http.schemas.admin_exhibits import (
    CreateExhibitRequest,
    ExhibitDraftRow,
)

LIST_FIELDS: Final = ("genres", "styles")
LIST_SEPARATOR: Final = ","
DRAFT_FIELD_BY_COMMAND_FIELD: Final = {
    "country_name": "country",
    "genre_names": "genres",
    "style_names": "styles",
}


class InvalidDraftsError(Exception):
    pass


def to_import_row(
    draft: ExhibitDraftRow,
) -> tuple[ExhibitImportRow | None, list[ExhibitImportIssue]]:
    values = draft.model_dump(exclude={"row_number"})
    for field in LIST_FIELDS:
        values[field] = _split_names(values[field])
    try:
        request = CreateExhibitRequest.model_validate(values)
    except ValidationError as error:
        return None, [
            ExhibitImportIssue(draft.row_number, str(detail["loc"][0]), detail["msg"])
            for detail in error.errors()
        ]
    return ExhibitImportRow(
        row_number=draft.row_number, exhibit=request.to_command()
    ), []


def to_import_rows(
    drafts: Sequence[ExhibitDraftRow], *, max_rows: int
) -> tuple[list[ExhibitImportRow], list[ExhibitImportIssue]]:
    if len(drafts) > max_rows:
        raise InvalidDraftsError(f"한 번에 {max_rows}행까지 등록할 수 있습니다.")
    row_numbers = [draft.row_number for draft in drafts]
    if len(set(row_numbers)) != len(row_numbers):
        raise InvalidDraftsError("행 번호가 중복되었습니다.")

    rows: list[ExhibitImportRow] = []
    issues: list[ExhibitImportIssue] = []
    for draft in drafts:
        row, row_issues = to_import_row(draft)
        if row is not None:
            rows.append(row)
        issues.extend(row_issues)
    return rows, issues


def from_sourced(item: SourcedExhibit, *, row_number: int) -> ExhibitDraftRow:
    return ExhibitDraftRow.model_validate(
        {
            "row_number": row_number,
            "title": item.title,
            "description": item.description,
            "poster_url": item.poster_url,
            "ticket_url": item.ticket_url,
            "start_date": item.start_date,
            "end_date": item.end_date,
            "exhibit_hall_name": item.place_name,
            "country": item.country,
            "region": item.region,
            "address": item.address,
            "phone": item.phone,
            "latitude": item.latitude,
            "longitude": item.longitude,
        }
    )


def _split_names(text: str | None) -> list[str]:
    if text is None:
        return []
    names = (name.strip() for name in text.split(LIST_SEPARATOR))
    return [name for name in names if name]
