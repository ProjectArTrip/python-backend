from io import BytesIO
from typing import Any

import pytest
from arttrip.inbound.http.exhibit_workbook import (
    EXHIBIT_COLUMNS,
    EXHIBIT_SHEET_TITLE,
    InvalidWorkbookError,
    read_import_sheet,
)
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

GENEROUS_EXPANDED_BYTES = 10 * 1024 * 1024
VALID_ROW: list[Any] = [
    "서울 현대미술",
    None,
    "2026-11-01",
    "2026-11-30",
    "한국",
    "서울",
    "새 전시관",
    "회화",
    None,
    None,
    None,
    37.5665,
    126.978,
    None,
    None,
    None,
]


def workbook_bytes(*rows: list[Any], header: list[str] | None = None) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    assert isinstance(sheet, Worksheet)
    sheet.title = EXHIBIT_SHEET_TITLE
    sheet.append(header if header is not None else list(EXHIBIT_COLUMNS))
    for row in rows:
        sheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def read(content: bytes, *, max_rows: int = 10) -> Any:
    return read_import_sheet(
        content, max_rows=max_rows, max_uncompressed_bytes=GENEROUS_EXPANDED_BYTES
    )


class TestReadImportSheet:
    def test_수식이_든_행은_등록하지_않고_오류로_알린다(self) -> None:
        # given
        formula_row = ["=1+1", *VALID_ROW[1:]]

        # when
        sheet = read(workbook_bytes(formula_row))

        # then
        assert sheet.rows == ()
        assert sheet.drafts[0].title is None
        assert [(issue.row_number, issue.field) for issue in sheet.issues] == [
            (2, "title")
        ]

    def test_열_이름이_양식과_다르면_읽지_않는다(self) -> None:
        # given
        swapped_header = list(EXHIBIT_COLUMNS)
        swapped_header[0], swapped_header[1] = swapped_header[1], swapped_header[0]

        # when, then
        with pytest.raises(InvalidWorkbookError):
            read(workbook_bytes(VALID_ROW, header=swapped_header))

    def test_행_수가_상한을_한_줄이라도_넘으면_읽지_않는다(self) -> None:
        # given
        max_rows = 2
        rows = [VALID_ROW] * (max_rows + 1)

        # when, then
        with pytest.raises(InvalidWorkbookError):
            read(workbook_bytes(*rows), max_rows=max_rows)

    def test_압축을_풀었을_때_상한을_넘으면_열지_않는다(self) -> None:
        # given
        content = workbook_bytes(VALID_ROW)
        tiny_limit = 1

        # when, then
        with pytest.raises(InvalidWorkbookError):
            read_import_sheet(content, max_rows=10, max_uncompressed_bytes=tiny_limit)

    def test_엑셀이_아닌_파일은_읽지_않는다(self) -> None:
        # given
        not_xlsx = b"title,description\n\xff\xfe"

        # when, then
        with pytest.raises(InvalidWorkbookError):
            read(not_xlsx)
