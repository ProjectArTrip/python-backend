import pytest
from arttrip.inbound.http.exhibit_drafts import InvalidDraftsError, to_import_rows
from arttrip.inbound.http.schemas.admin_exhibits import ExhibitDraftRow


def draft(row_number: int) -> ExhibitDraftRow:
    return ExhibitDraftRow.model_validate({"row_number": row_number})


class TestToImportRows:
    def test_행_번호가_중복되면_거절한다(self) -> None:
        # given
        drafts = [draft(2), draft(2)]

        # when, then
        with pytest.raises(InvalidDraftsError):
            to_import_rows(drafts, max_rows=10)

    def test_행_수가_상한을_한_줄이라도_넘으면_거절한다(self) -> None:
        # given
        drafts = [draft(number) for number in range(2, 2 + 11)]

        # when, then
        with pytest.raises(InvalidDraftsError):
            to_import_rows(drafts, max_rows=10)
