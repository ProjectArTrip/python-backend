from collections.abc import Sequence
from typing import Final

from fastapi import APIRouter, HTTPException, Response, UploadFile
from pydantic.alias_generators import to_camel

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.port.input.exhibit.results import (
    ExhibitImportIssue,
)
from arttrip.common import settings
from arttrip.inbound.http.dependencies.exhibit import (
    FetchOpenDataExhibitsUseCaseDep,
    GetExhibitImportGuideUseCaseDep,
    ImportExhibitsUseCaseDep,
    PreviewExhibitImportUseCaseDep,
)
from arttrip.inbound.http.exhibit_drafts import (
    DRAFT_FIELD_BY_COMMAND_FIELD,
    InvalidDraftsError,
    from_sourced,
    to_import_rows,
)
from arttrip.inbound.http.exhibit_workbook import (
    TEMPLATE_FILENAME,
    XLSX_MEDIA_TYPE,
    ExhibitImportSheet,
    InvalidWorkbookError,
    build_import_template,
    read_import_sheet,
)
from arttrip.inbound.http.openapi import ADMIN_ERRORS, error_responses
from arttrip.inbound.http.pagination import PageIndexParam
from arttrip.inbound.http.schemas.admin_exhibits import (
    ExhibitDraftRow,
    ExhibitImportErrorResponse,
    ExhibitImportPreviewResponse,
    ExhibitImportPreviewRowResponse,
    ExhibitImportRequest,
    ExhibitImportResponse,
    ImportRowStatus,
)

router = APIRouter()

XLSX_SUFFIX: Final = ".xlsx"


@router.get(
    "/import/template",
    response_class=Response,
    responses={
        200: {
            "description": "전시 일괄 등록 엑셀 양식",
            "content": {XLSX_MEDIA_TYPE: {}},
        },
        **error_responses(*ADMIN_ERRORS),
    },
)
def download_exhibit_import_template(
    use_case: GetExhibitImportGuideUseCaseDep,
) -> Response:
    guide = use_case.get_exhibit_import_guide()
    return Response(
        content=build_import_template(guide),
        media_type=XLSX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{TEMPLATE_FILENAME}"'},
    )


@router.post(
    "/import/preview",
    response_model=ExhibitImportPreviewResponse,
    responses=error_responses(*ADMIN_ERRORS),
)
def preview_exhibit_import(
    file: UploadFile,
    use_case: PreviewExhibitImportUseCaseDep,
) -> ExhibitImportPreviewResponse:
    sheet = _read_upload(file)
    preview = use_case.preview_exhibit_import(sheet.rows)
    return _to_preview_response(
        sheet.drafts,
        issues=[*sheet.issues, *preview.issues],
        duplicate_row_numbers=preview.duplicate_row_numbers,
    )


@router.post(
    "/import",
    status_code=201,
    response_model=ExhibitImportResponse,
    responses=error_responses(*ADMIN_ERRORS),
)
def import_exhibits(
    body: ExhibitImportRequest,
    use_case: ImportExhibitsUseCaseDep,
) -> ExhibitImportResponse:

    try:
        rows, issues = to_import_rows(
            body.rows, max_rows=settings.exhibit.import_max_rows
        )
    except InvalidDraftsError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if issues:
        raise _reject_import(issues)

    result = use_case.import_exhibits(rows)

    if result.issues:
        raise _reject_import(result.issues)
    return ExhibitImportResponse(
        created_count=len(result.exhibit_ids),
        exhibit_ids=list(result.exhibit_ids),
        skipped_count=len(result.skipped_row_numbers),
    )


@router.get(
    "/opendata/preview",
    response_model=ExhibitImportPreviewResponse,
    responses=error_responses(*ADMIN_ERRORS, ExhibitError.source_unavailable),
)
def preview_open_data_exhibits(
    fetch_use_case: FetchOpenDataExhibitsUseCaseDep,
    preview_use_case: PreviewExhibitImportUseCaseDep,
    page: PageIndexParam = 0,
) -> ExhibitImportPreviewResponse:

    sourced = fetch_use_case.fetch_open_data_exhibits(page)
    first_row_number = page * settings.opendata.page_size + 1

    drafts = [
        from_sourced(item, row_number=first_row_number + index)
        for index, item in enumerate(sourced.items)
    ]

    rows, draft_issues = to_import_rows(
        drafts, max_rows=settings.exhibit.import_max_rows
    )

    preview = preview_use_case.preview_exhibit_import(rows)

    response = _to_preview_response(
        drafts,
        issues=[*draft_issues, *preview.issues],
        duplicate_row_numbers=preview.duplicate_row_numbers,
    )

    return response.model_copy(update={"source_total_count": sourced.total_count})


def _read_upload(file: UploadFile) -> ExhibitImportSheet:
    if not (file.filename or "").lower().endswith(XLSX_SUFFIX):
        raise HTTPException(
            status_code=400, detail="엑셀(.xlsx) 파일만 올릴 수 있습니다."
        )
    limits = settings.exhibit
    content = file.file.read(limits.import_max_bytes + 1)
    if len(content) > limits.import_max_bytes:
        raise HTTPException(status_code=413, detail="파일이 너무 큽니다.")
    try:
        return read_import_sheet(
            content,
            max_rows=limits.import_max_rows,
            max_uncompressed_bytes=limits.import_max_uncompressed_bytes,
        )
    except InvalidWorkbookError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _to_preview_response(
    drafts: Sequence[ExhibitDraftRow],
    *,
    issues: Sequence[ExhibitImportIssue],
    duplicate_row_numbers: Sequence[int],
) -> ExhibitImportPreviewResponse:
    invalid_rows = {issue.row_number for issue in issues}
    duplicate_rows = set(duplicate_row_numbers)
    return ExhibitImportPreviewResponse(
        total_count=len(drafts),
        rows=[
            ExhibitImportPreviewRowResponse.model_validate(
                {
                    **draft.model_dump(),
                    "status": _status_of(
                        draft.row_number, invalid_rows, duplicate_rows
                    ),
                }
            )
            for draft in drafts
        ],
        duplicate_rows=sorted(duplicate_rows),
        errors=_to_error_responses(issues),
    )


def _status_of(
    row_number: int, invalid_rows: set[int], duplicate_rows: set[int]
) -> ImportRowStatus:
    if row_number in invalid_rows:
        return ImportRowStatus.INVALID
    if row_number in duplicate_rows:
        return ImportRowStatus.DUPLICATE
    return ImportRowStatus.VALID


def _field_of(field: str | None) -> str | None:
    if field is None:
        return None
    return to_camel(DRAFT_FIELD_BY_COMMAND_FIELD.get(field, field))


def _to_error_responses(
    issues: Sequence[ExhibitImportIssue],
) -> list[ExhibitImportErrorResponse]:
    return [
        ExhibitImportErrorResponse(
            row=issue.row_number, field=_field_of(issue.field), message=issue.message
        )
        for issue in sorted(issues, key=lambda issue: issue.row_number)
    ]


def _reject_import(issues: Sequence[ExhibitImportIssue]) -> HTTPException:
    errors = _to_error_responses(issues)
    return HTTPException(
        status_code=400,
        detail=[error.model_dump(by_alias=True) for error in errors],
    )
