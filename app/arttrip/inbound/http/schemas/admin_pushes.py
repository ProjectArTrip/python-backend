from typing import Annotated, Final

from pydantic import Field

from arttrip.application.domain.notification.notification import (
    BODY_MAX_LENGTH,
    TITLE_MAX_LENGTH,
)
from arttrip.application.domain.notification.notification_action import (
    NotificationAction,
)
from arttrip.inbound.http.schemas.base import ApiModel

MAX_PUSH_USERS: Final = 500


class PushMessageRequest(ApiModel):
    title: str = Field(min_length=1, max_length=TITLE_MAX_LENGTH)
    body: str = Field(min_length=1, max_length=BODY_MAX_LENGTH)
    action: NotificationAction = NotificationAction.NONE
    reference_id: int | None = Field(default=None, gt=0)

    def to_data(self) -> dict[str, str]:
        data = {"action": self.action.value}
        if self.reference_id is not None:
            data["referenceId"] = str(self.reference_id)
        return data


class BulkPushRequest(PushMessageRequest):
    user_ids: list[Annotated[int, Field(gt=0)]] = Field(
        min_length=1, max_length=MAX_PUSH_USERS
    )


class PushDispatchResponse(ApiModel):
    dispatch_id: int | None
    requested_users: int
    targeted_tokens: int
    succeeded: int
    failed: int
    removed_tokens: int


class BurstPushRequest(PushMessageRequest):
    count: int = Field(ge=1, le=MAX_PUSH_USERS)
