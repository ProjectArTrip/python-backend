from collections.abc import Callable
from typing import Any

from fastapi import Request

from arttrip.application.port.output.unit_of_work import UnitOfWork
from arttrip.outbound.persistence.unit_of_work import SqlAlchemyUnitOfWork

Overrides = dict[Callable[..., Any], Callable[..., Any]]


def new_unit_of_work(request: Request) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(request.app.state.session_factory)
