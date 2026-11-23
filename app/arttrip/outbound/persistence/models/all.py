from arttrip.outbound.persistence.models.artist_application import (
    map_artist_application_table,
)
from arttrip.outbound.persistence.models.country import (
    map_country_table,
)
from arttrip.outbound.persistence.models.curation import (
    map_curation_exhibit_table,
    map_curation_table,
)
from arttrip.outbound.persistence.models.exhibit import map_exhibit_table
from arttrip.outbound.persistence.models.exhibit_hall import map_exhibit_hall_table
from arttrip.outbound.persistence.models.favorite import map_favorite_table
from arttrip.outbound.persistence.models.keyword import map_keyword_table
from arttrip.outbound.persistence.models.push_dispatch import (
    map_push_delivery_table,
    map_push_dispatch_table,
)
from arttrip.outbound.persistence.models.region import map_region_table
from arttrip.outbound.persistence.models.review import map_review_table
from arttrip.outbound.persistence.models.review_image import map_review_image_table
from arttrip.outbound.persistence.models.search_history import map_search_history_table
from arttrip.outbound.persistence.models.social_account import map_social_accounts_table
from arttrip.outbound.persistence.models.user import map_users_table
from arttrip.outbound.persistence.models.user_keyword import map_user_keyword_table
from arttrip.outbound.persistence.models.user_notice import map_user_notice_table


def map_tables() -> None:
    map_users_table()
    map_social_accounts_table()
    map_keyword_table()
    map_user_keyword_table()
    map_exhibit_hall_table()
    map_exhibit_table()
    map_artist_application_table()
    map_user_notice_table()
    map_favorite_table()
    map_curation_table()
    map_country_table()
    map_region_table()
    map_curation_exhibit_table()
    map_search_history_table()
    map_push_dispatch_table()
    map_push_delivery_table()
    map_review_table()
    map_review_image_table()
