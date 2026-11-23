from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Final

from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.review.exceptions import ReviewError
from arttrip.application.util.exception import DomainException

_DOMAIN_ERRORS: Final[dict[str, Callable[[], DomainException]]] = {
    "uq_exhibit_exhibit_hall_id_title_start_date": ExhibitError.duplicate,
    "uq_review_user_id_exhibit_id": ReviewError.already_written,
}


@contextmanager
def translate_integrity_errors() -> Iterator[None]:
    try:
        yield
    except IntegrityError as error:
        cause = error.orig
        if isinstance(cause, UniqueViolation):
            to_domain = _DOMAIN_ERRORS.get(cause.diag.constraint_name or "")
            if to_domain is not None:
                raise to_domain() from error
        raise
