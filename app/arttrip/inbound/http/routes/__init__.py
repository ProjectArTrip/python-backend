from fastapi import APIRouter

from arttrip.inbound.http.api_prefix import API_V1_STR
from arttrip.inbound.http.routes import (
    artist_applications,
    artist_exhibits,
    auth,
    curations,
    exhibits,
    favorites,
    home,
    keywords,
    notifications,
    onboarding,
    recent_exhibits,
    reviews,
    search_history,
    users,
    web_auth,
)
from arttrip.inbound.http.routes.admin import admin_router

root_router = APIRouter(prefix=API_V1_STR)
root_router.include_router(admin_router)
root_router.include_router(auth.router, prefix="/auth", tags=["auth"])
root_router.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])
root_router.include_router(users.router, prefix="/users", tags=["users"])
root_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
root_router.include_router(exhibits.router, prefix="/exhibits", tags=["exhibits"])
root_router.include_router(
    artist_applications.router,
    prefix="/users/me/artistRequest",
    tags=["artist"],
)

root_router.include_router(
    notifications.router,
    prefix="/users/me/notifications",
    tags=["notifications"],
)
root_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
root_router.include_router(home.router, prefix="/home/exhibits", tags=["home"])
root_router.include_router(
    recent_exhibits.router,
    prefix="/users/me/recentExhibits",
    tags=["exhibits"],
)

root_router.include_router(curations.router, prefix="/curations", tags=["curations"])
root_router.include_router(web_auth.router, prefix="/oauth2", tags=["auth"])
root_router.include_router(
    search_history.router,
    prefix="/users/me/searchHistory",
    tags=["searchHistory"],
)
root_router.include_router(
    artist_exhibits.router,
    prefix="/artist/exhibits",
    tags=["artist"],
)

root_router.include_router(reviews.router, tags=["reviews"])
