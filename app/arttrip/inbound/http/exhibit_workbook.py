import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from io import BytesIO
from itertools import zip_longest
from tempfile import NamedTemporaryFile
from typing import Any, Final

from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl.worksheet._read_only import ReadOnlyWorksheet
from openpyxl.worksheet.worksheet import Worksheet

from arttrip.application.port.input.exhibit.commands import ExhibitImportRow
from arttrip.application.port.input.exhibit.results import (
    ExhibitImportGuide,
    ExhibitImportIssue,
)
from arttrip.inbound.http.exhibit_drafts import to_import_row
from arttrip.inbound.http.schemas.admin_exhibits import ExhibitDraftRow

XLSX_MEDIA_TYPE: Final = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

TEMPLATE_FILENAME: Final = "exhibit-import-template.xlsx"
EXHIBIT_SHEET_TITLE: Final = "전시"
GUIDE_SHEET_TITLE: Final = "가이드"
EXHIBIT_COLUMNS: Final[dict[str, str]] = {
    "제목*": "title",
    "설명": "description",
    "전시 시작": "start_date",
    "전시 종료": "end_date",
    "국가*": "country",
    "지역*": "region",
    "장소(건물명)*": "exhibit_hall_name",
    "장르": "genres",
    "전시 스타일": "styles",
    "예약링크": "ticket_url",
    "이미지": "poster_url",
    "위도*": "latitude",
    "경도*": "longitude",
    "전화번호": "phone",
    "영업시간": "opening_hours",
    "주소": "address",
}
GUIDE_COLUMNS: Final = ("국가", "국내 지역", "장르", "전시 스타일")
FORMULA_DATA_TYPE: Final = "f"
HEADER_ROW_NUMBER: Final = 1


class InvalidWorkbookError(Exception):
    pass


@dataclass(frozen=True)
class ExhibitImportSheet:
    total_count: int
    rows: tuple[ExhibitImportRow, ...]
    issues: tuple[ExhibitImportIssue, ...]
    drafts: tuple[ExhibitDraftRow, ...]


def build_import_template(guide: ExhibitImportGuide) -> bytes:
    workbook = Workbook()
    exhibit_sheet = workbook.active
    if not isinstance(exhibit_sheet, Worksheet):
        raise RuntimeError("a new workbook must start with one worksheet")
    exhibit_sheet.title = EXHIBIT_SHEET_TITLE
    exhibit_sheet.append(list(EXHIBIT_COLUMNS))

    guide_sheet = workbook.create_sheet(GUIDE_SHEET_TITLE)
    guide_sheet.append(list(GUIDE_COLUMNS))
    guide_rows = zip_longest(
        guide.country_names,
        guide.region_names,
        guide.genre_names,
        guide.style_names,
    )
    for row in guide_rows:
        guide_sheet.append(list(row))

    with NamedTemporaryFile(suffix=".xlsx") as tmp:
        workbook.save(tmp.name)
        tmp.seek(0)
        return tmp.read()


def read_import_sheet(
    content: bytes, *, max_rows: int, max_uncompressed_bytes: int
) -> ExhibitImportSheet:
    _ensure_expandable(content, max_uncompressed_bytes=max_uncompressed_bytes)
    try:
        workbook = load_workbook(BytesIO(content), read_only=True)
    except (InvalidFileException, zipfile.BadZipFile, KeyError, ValueError) as error:
        raise InvalidWorkbookError("엑셀(.xlsx) 파일을 읽을 수 없습니다.") from error
    try:
        return _read_exhibit_sheet(workbook, max_rows=max_rows)
    finally:
        workbook.close()


def _read_exhibit_sheet(workbook: Any, *, max_rows: int) -> ExhibitImportSheet:
    if EXHIBIT_SHEET_TITLE not in workbook.sheetnames:
        raise InvalidWorkbookError(
            f"'{EXHIBIT_SHEET_TITLE}' 시트가 없습니다. 양식을 다시 내려받아 주세요."
        )
    sheet = workbook[EXHIBIT_SHEET_TITLE]
    if not isinstance(sheet, ReadOnlyWorksheet):
        raise InvalidWorkbookError(f"'{EXHIBIT_SHEET_TITLE}' 시트를 읽을 수 없습니다.")

    sheet_rows = sheet.rows
    header = [cell.value for cell in next(sheet_rows, ())]
    if header[: len(EXHIBIT_COLUMNS)] != list(EXHIBIT_COLUMNS):
        raise InvalidWorkbookError(
            "열 이름이 양식과 다릅니다. 양식을 다시 내려받아 주세요."
        )

    drafts: list[ExhibitDraftRow] = []
    rows: list[ExhibitImportRow] = []
    issues: list[ExhibitImportIssue] = []
    data_row_count = 0
    for row_number, cells in enumerate(sheet_rows, start=HEADER_ROW_NUMBER + 1):
        if all(cell.value is None for cell in cells):
            continue
        data_row_count += 1
        if data_row_count > max_rows:
            raise InvalidWorkbookError(f"한 번에 {max_rows}행까지 등록할 수 있습니다.")
        draft, formula_issues = _read_draft(row_number, cells)
        drafts.append(draft)
        if formula_issues:
            issues.extend(formula_issues)
            continue
        row, row_issues = to_import_row(draft)
        if row is not None:
            rows.append(row)
        issues.extend(row_issues)
    return ExhibitImportSheet(
        total_count=data_row_count,
        drafts=tuple(drafts),
        rows=tuple(rows),
        issues=tuple(issues),
    )


def _ensure_expandable(content: bytes, *, max_uncompressed_bytes: int) -> None:
    try:
        with zipfile.ZipFile(BytesIO(content)) as archive:
            expanded_bytes = sum(info.file_size for info in archive.infolist())
    except zipfile.BadZipFile as error:
        raise InvalidWorkbookError("엑셀(.xlsx) 파일을 읽을 수 없습니다.") from error
    if expanded_bytes > max_uncompressed_bytes:
        raise InvalidWorkbookError("압축을 풀면 너무 커지는 파일이라 열 수 없습니다.")


def _read_draft(
    row_number: int, cells: tuple[Any, ...]
) -> tuple[ExhibitDraftRow, list[ExhibitImportIssue]]:
    values: dict[str, object] = {"row_number": row_number}
    issues: list[ExhibitImportIssue] = []
    for column, cell in zip(EXHIBIT_COLUMNS, cells):
        field = EXHIBIT_COLUMNS[column]
        if getattr(cell, "data_type", None) == FORMULA_DATA_TYPE:
            issues.append(
                ExhibitImportIssue(
                    row_number,
                    field,
                    "수식은 쓸 수 없습니다. 값만 입력해 주세요.",
                )
            )
            continue
        values[field] = _to_draft_value(cell.value)
    return ExhibitDraftRow.model_validate(values), issues


def _to_draft_value(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    return text or None
