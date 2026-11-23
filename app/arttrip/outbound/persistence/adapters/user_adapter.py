from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from arttrip.application.domain.auth.social_provider import SocialProvider
from arttrip.application.domain.user.role import UserRole
from arttrip.application.domain.user.user import User
from arttrip.application.port.output.user_port import UserPort
from arttrip.outbound.persistence.models import (
    artist_application_table,
    favorite_table,
    push_delivery_table,
    recent_exhibit_table,
    review_image_table,
    review_table,
    search_history_table,
    social_accounts_table,
    user_keyword_table,
    user_notice_table,
    users_table,
)


class UserAdapter(UserPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> None:
        self._session.add(user)
        self._session.flush()

    def find_by_social_identity(
        self, *, provider: SocialProvider, provider_user_id: str
    ) -> User | None:
        statement = (
            select(User)
            .join(
                social_accounts_table,
                social_accounts_table.c.user_id == users_table.c.id,
            )
            .where(
                social_accounts_table.c.provider == provider,
                social_accounts_table.c.provider_user_id == provider_user_id,
            )
        )
        return self._session.scalars(statement).one_or_none()

    def find_by_id(self, user_id: int) -> User | None:
        return self._session.get(User, user_id)

    def find_by_id_for_update(self, user_id: int) -> User | None:
        return self._session.get(User, user_id, with_for_update=True)

    def is_nickname_taken(self, *, nickname: str, except_user_id: int) -> bool:
        statement = (
            select(users_table.c.id)
            .where(
                func.lower(users_table.c.nickname) == nickname.lower(),
                users_table.c.id != except_user_id,
            )
            .limit(1)
        )
        return self._session.scalar(statement) is not None

    def find_ids_by_role(self, role: UserRole) -> list[int]:
        statement = select(users_table.c.id).where(users_table.c.role == role)
        return list(self._session.scalars(statement).all())

    def remove_with_owned_data(self, user_id: int) -> None:
        user_reviews = select(review_table.c.id).where(
            review_table.c.user_id == user_id
        )
        self._session.execute(
            delete(review_image_table).where(
                review_image_table.c.review_id.in_(user_reviews)
            )
        )
        owned_tables = (
            push_delivery_table,
            review_table,
            favorite_table,
            recent_exhibit_table,
            search_history_table,
            user_notice_table,
            user_keyword_table,
            artist_application_table,
            social_accounts_table,
        )
        for table in owned_tables:
            self._session.execute(delete(table).where(table.c.user_id == user_id))
        self._session.execute(delete(users_table).where(users_table.c.id == user_id))
