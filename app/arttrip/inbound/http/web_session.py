from dataclasses import dataclass
from typing import Annotated, Final, Literal

from fastapi import Depends, Request, Response

from arttrip.application.domain.auth.exceptions import AuthError
from arttrip.inbound.http.api_prefix import API_V1_STR

ACCESS_TOKEN_COOKIE: Final = "accessToken"
REFRESH_TOKEN_COOKIE: Final = "refreshToken"
STATE_COOKIE: Final = "oauth_state"
NONCE_COOKIE: Final = "oauth_nonce"

REFRESH_TOKEN_COOKIE_PATH: Final = f"{API_V1_STR}/auth/web"
SIGN_IN_COOKIE_PATH: Final = f"{API_V1_STR}/oauth2"

SAFE_METHODS: Final = frozenset({"GET", "HEAD", "OPTIONS"})


@dataclass(frozen=True)
class WebSessionPolicy:
    secure: bool
    samesite: Literal["lax", "strict", "none"]
    access_max_age_seconds: int
    refresh_max_age_seconds: int
    state_max_age_seconds: int
    success_redirect_url: str
    failure_redirect_url: str
    allowed_origins: frozenset[str]


def get_web_session_policy(request: Request) -> WebSessionPolicy:
    policy: WebSessionPolicy = request.app.state.web_session_policy
    return policy


WebSessionPolicyDep = Annotated[WebSessionPolicy, Depends(get_web_session_policy)]


def set_sign_in_cookies(
    response: Response, *, policy: WebSessionPolicy, state: str, nonce: str
) -> None:
    for key, value in ((STATE_COOKIE, state), (NONCE_COOKIE, nonce)):
        response.set_cookie(
            key=key,
            value=value,
            max_age=policy.state_max_age_seconds,
            path=SIGN_IN_COOKIE_PATH,
            secure=policy.secure,
            httponly=True,
            samesite="lax",
        )


def ensure_trusted_origin(request: Request, *, policy: WebSessionPolicy) -> None:
    if request.method in SAFE_METHODS:
        return
    origin = request.headers.get("origin")
    if origin is None or origin not in policy.allowed_origins:
        raise AuthError.untrusted_origin()


def clear_sign_in_cookies(response: Response, *, policy: WebSessionPolicy) -> None:
    for key in (STATE_COOKIE, NONCE_COOKIE):
        response.delete_cookie(
            key=key,
            path=SIGN_IN_COOKIE_PATH,
            secure=policy.secure,
            httponly=True,
            samesite="lax",
        )


def set_token_cookies(
    response: Response,
    *,
    policy: WebSessionPolicy,
    access_token: str,
    refresh_token: str,
) -> None:
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        max_age=policy.access_max_age_seconds,
        path="/",
        secure=policy.secure,
        httponly=True,
        samesite=policy.samesite,
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        max_age=policy.refresh_max_age_seconds,
        path=REFRESH_TOKEN_COOKIE_PATH,
        secure=policy.secure,
        httponly=True,
        samesite=policy.samesite,
    )


def clear_token_cookies(response: Response, *, policy: WebSessionPolicy) -> None:
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE,
        path="/",
        secure=policy.secure,
        httponly=True,
        samesite=policy.samesite,
    )
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE,
        path=REFRESH_TOKEN_COOKIE_PATH,
        secure=policy.secure,
        httponly=True,
        samesite=policy.samesite,
    )
