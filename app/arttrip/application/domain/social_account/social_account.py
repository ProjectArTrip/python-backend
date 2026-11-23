from datetime import datetime

from arttrip.application.domain.auth.social_provider import SocialProvider
from arttrip.application.domain.social_account.exceptions import SocialAccountError
from arttrip.application.util.utc import to_utc


class SocialAccount:
    def __init__(
        self,
        *,
        id_: int | None,
        provider: SocialProvider,
        provider_user_id: str,
        linked_at: datetime,
    ) -> None:
        if not provider_user_id.strip():
            raise SocialAccountError.blank_provider_user_id()
        self._id = id_
        self.provider = provider
        self.provider_user_id = provider_user_id
        self.linked_at = to_utc(linked_at)

    @property
    def id(self) -> int | None:
        return self._id
