from typing import Collection

from sqlalchemy import ColumnElement, select, update
from sqlalchemy.orm import Session

from arttrip.application.port.output.device_token_port import (
    DeviceTokenPort,
    PushTarget,
)
from arttrip.outbound.persistence.models import users_table


class DeviceTokenAdapter(DeviceTokenPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def assign_to_user(self, *, user_id: int, token: str) -> None:
        release_from_others = (
            update(users_table)
            .where(users_table.c.fcm_token == token, users_table.c.id != user_id)
            .values(fcm_token=None)
        )
        assign_to_user = (
            update(users_table)
            .where(users_table.c.id == user_id)
            .values(fcm_token=token)
        )
        self._session.execute(release_from_others)
        self._session.execute(assign_to_user)

    def clear_for_user(self, user_id: int) -> None:
        statement = (
            update(users_table)
            .where(users_table.c.id == user_id)
            .values(fcm_token=None)
        )
        self._session.execute(statement)

    def find_push_targets(self, user_ids: Collection[int]) -> list[PushTarget]:
        return self._push_targets(users_table.c.id.in_(user_ids))

    def clear_tokens(self, tokens: Collection[str]) -> None:
        statement = (
            update(users_table)
            .where(users_table.c.fcm_token.in_(tokens))
            .values(fcm_token=None)
        )
        self._session.execute(statement)

    def find_all_push_targets(self) -> list[PushTarget]:
        return self._push_targets()

    def _push_targets(self, *conditions: ColumnElement[bool]) -> list[PushTarget]:
        statement = select(users_table.c.id, users_table.c.fcm_token).where(
            users_table.c.push_enabled.is_(True),
            users_table.c.fcm_token.is_not(None),
            *conditions,
        )
        return [
            PushTarget(user_id=user_id, token=token)
            for user_id, token in self._session.execute(statement)
            if token
        ]
