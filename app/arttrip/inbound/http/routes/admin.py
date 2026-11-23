from fastapi import APIRouter, Depends

from arttrip.inbound.http.dependencies.auth import require_admin
from arttrip.inbound.http.routes import (
    admin_artist_applications,
    admin_curations,
    admin_exhibit_imports,
    admin_exhibits,
    admin_pushes,
)

admin_router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
admin_router.include_router(
    admin_artist_applications.router,
    prefix="/artistRequests",
    tags=["adminArtistRequests"],
)
admin_router.include_router(
    admin_exhibit_imports.router,
    prefix="/exhibits",
    tags=["adminExhibits"],
)
admin_router.include_router(
    admin_exhibits.router,
    prefix="/exhibits",
    tags=["adminExhibits"],
)

admin_router.include_router(
    admin_curations.router,
    prefix="/curations",
    tags=["adminCurations"],
)
admin_router.include_router(
    admin_pushes.router,
    prefix="/push",
    tags=["pushTest"],
)
