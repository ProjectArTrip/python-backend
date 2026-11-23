import importlib
import pkgutil
from collections.abc import Callable
from typing import Any

from fastapi import FastAPI

from arttrip.bootstrap.wiring.artist_application import wire_artist_application
from arttrip.bootstrap.wiring.auth import wire_auth
from arttrip.bootstrap.wiring.curation import wire_curation
from arttrip.bootstrap.wiring.exhibit import wire_exhibit
from arttrip.bootstrap.wiring.favorite import wire_favorite
from arttrip.bootstrap.wiring.home import wire_home
from arttrip.bootstrap.wiring.keyword import wire_keyword
from arttrip.bootstrap.wiring.location import wire_location
from arttrip.bootstrap.wiring.notification import wire_notification
from arttrip.bootstrap.wiring.review import wire_review
from arttrip.bootstrap.wiring.search_history import wire_search_history
from arttrip.bootstrap.wiring.user import wire_user
from arttrip.inbound.http import dependencies as http_dependencies


def _collect_placeholders() -> set[Callable[..., Any]]:
    placeholders: set[Callable[..., Any]] = set()
    for module_info in pkgutil.iter_modules(http_dependencies.__path__):
        module = importlib.import_module(
            f"{http_dependencies.__name__}.{module_info.name}"
        )
        placeholders.update(
            value
            for name, value in vars(module).items()
            if name.startswith("provide_") and callable(value)
        )
    return placeholders


def _assert_all_provided(app: FastAPI) -> None:
    missing = sorted(
        fn.__name__
        for fn in _collect_placeholders().difference(app.dependency_overrides)
    )
    if missing:
        raise RuntimeError(f"dependencies not wired: {', '.join(missing)}")


def wire(app: FastAPI) -> None:
    overrides = app.dependency_overrides
    wire_notification(overrides)
    wire_user(overrides)
    wire_keyword(overrides)
    wire_location(overrides)
    wire_exhibit(overrides)
    wire_artist_application(overrides)
    wire_auth(overrides)
    wire_favorite(overrides)
    wire_home(overrides)
    wire_curation(overrides)
    wire_search_history(overrides)
    wire_review(overrides)
    _assert_all_provided(app)
