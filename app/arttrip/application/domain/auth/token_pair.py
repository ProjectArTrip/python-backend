from datetime import datetime

from arttrip.application.domain.user.role import UserRole
from arttrip.application.port.input.auth.results import TokenPair
from arttrip.application.port.output.refresh_token_port import RefreshTokenPort
from arttrip.application.port.output.token_port import TokenPort


def issue_token_pair(
    *,
    tokens: TokenPort,
    refresh_tokens: RefreshTokenPort,
    user_id: int,
    role: UserRole,
    now: datetime,
) -> TokenPair:
    return TokenPair(
        access_token=tokens.issue_access_token(user_id=user_id, role=role, now=now),
        refresh_token=refresh_tokens.issue(user_id=user_id),
    )
