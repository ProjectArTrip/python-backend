from arttrip.outbound.persistence.models.artist_application import (
    artist_application_table,
)
from arttrip.outbound.persistence.models.banned_word import banned_word_table
from arttrip.outbound.persistence.models.country import (
    country_alias_table,
    country_table,
)
from arttrip.outbound.persistence.models.curation import (
    curation_exhibit_table,
    curation_table,
)
from arttrip.outbound.persistence.models.exhibit import (
    exhibit_keyword_table,
    exhibit_table,
)
from arttrip.outbound.persistence.models.exhibit_hall import exhibit_hall_table
from arttrip.outbound.persistence.models.exhibit_sync import exhibit_sync_table
from arttrip.outbound.persistence.models.favorite import favorite_table
from arttrip.outbound.persistence.models.keyword import keyword_table
from arttrip.outbound.persistence.models.maintenance import maintenance_table
from arttrip.outbound.persistence.models.notice import notice_table
from arttrip.outbound.persistence.models.push_dispatch import (
    push_delivery_table,
    push_dispatch_table,
)
from arttrip.outbound.persistence.models.recent_exhibit import (
    recent_exhibit_table,
)
from arttrip.outbound.persistence.models.region import region_table
from arttrip.outbound.persistence.models.review import review_table
from arttrip.outbound.persistence.models.review_image import review_image_table
from arttrip.outbound.persistence.models.search_history import (
    search_history_table,
)
from arttrip.outbound.persistence.models.social_account import (
    social_accounts_table,
)
from arttrip.outbound.persistence.models.user import users_table
from arttrip.outbound.persistence.models.user_keyword import user_keyword_table
from arttrip.outbound.persistence.models.user_notice import user_notice_table

__all__ = [
    "artist_application_table",
    "banned_word_table",
    "country_table",
    "country_alias_table",
    "curation_exhibit_table",
    "curation_table",
    "exhibit_hall_table",
    "exhibit_keyword_table",
    "exhibit_sync_table",
    "exhibit_table",
    "favorite_table",
    "keyword_table",
    "maintenance_table",
    "notice_table",
    "recent_exhibit_table",
    "region_table",
    "review_image_table",
    "review_table",
    "search_history_table",
    "social_accounts_table",
    "user_keyword_table",
    "user_notice_table",
    "users_table",
    "push_delivery_table",
    "push_dispatch_table",
]
