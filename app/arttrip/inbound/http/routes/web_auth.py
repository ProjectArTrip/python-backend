import secrets
from typing import Annotated, Final
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from fastapi import APIRouter, Cookie, Query
from fastapi.responses import RedirectResponse

from arttrip.application.domain.auth.exceptions import AuthError
from arttrip.application.domain.auth.social_provider import SocialProvider
from arttrip.application.port.input.auth.commands import CompleteWebSignInCommand
from arttrip.inbound.http.dependencies.auth import (
    CompleteWebSignInUseCaseDep,
    StartWebSignInUseCaseDep,
)
from arttrip.inbound.http.openapi import error_responses
from arttrip.inbound.http.web_session import (
    WebSessionPolicy,
    WebSessionPolicyDep,
    clear_sign_in_cookies,
    set_sign_in_cookies,
    set_token_cookies,
)

router = APIRouter()

CODE_MAX_LENGTH: Final = 2048
STATE_MAX_LENGTH: Final = 256


def _to_provider(value: str) -> SocialProvider:
    try:
        return SocialProvider(value.upper())
    except ValueError as error:
        raise AuthError.unsupported_web_provider() from error


def _redirect_to_failure(
    policy: WebSessionPolicy, error: AuthError
) -> RedirectResponse:
    parts = urlsplit(policy.failure_redirect_url)
    query = urlencode([*parse_qsl(parts.query), ("error", error.code)])
    response = RedirectResponse(
        urlunsplit(parts._replace(query=query)), status_code=302
    )
    clear_sign_in_cookies(response, policy=policy)
    response.headers["Cache-Control"] = "no-store"
    return response


@router.get("/authorization/{provider}", status_code=302)
def start_web_sign_in(
    provider: str,
    use_case: StartWebSignInUseCaseDep,
    policy: WebSessionPolicyDep,
) -> RedirectResponse:
    try:
        start = use_case.start_web_sign_in(_to_provider(provider))
    except AuthError as error:
        return _redirect_to_failure(policy, error)
    response = RedirectResponse(start.authorization_url, status_code=302)
    set_sign_in_cookies(response, policy=policy, state=start.state, nonce=start.nonce)
    response.headers["Cache-Control"] = "no-store"
    return response


@router.get(
    "/callback/{provider}",
    status_code=302,
    responses=error_responses(
        AuthError.unsupported_web_provider,
        AuthError.invalid_web_sign_in_request,
        AuthError.invalid_id_token,
        AuthError.provider_unavailable,
        AuthError.web_sign_in_not_allowed,
    ),
)
@router.get("/callback/{provider}", status_code=302)
def complete_web_sign_in(
    provider: str,
    use_case: CompleteWebSignInUseCaseDep,
    policy: WebSessionPolicyDep,
    code: Annotated[str | None, Query(max_length=CODE_MAX_LENGTH)] = None,
    state: Annotated[str | None, Query(max_length=STATE_MAX_LENGTH)] = None,
    oauth_state: Annotated[str | None, Cookie(max_length=STATE_MAX_LENGTH)] = None,
    oauth_nonce: Annotated[str | None, Cookie(max_length=STATE_MAX_LENGTH)] = None,
) -> RedirectResponse:
    try:
        if code is None or state is None or oauth_state is None or oauth_nonce is None:
            raise AuthError.invalid_web_sign_in_request()
        if not secrets.compare_digest(state.encode(), oauth_state.encode()):
            raise AuthError.invalid_web_sign_in_request()
        tokens = use_case.complete_web_sign_in(
            CompleteWebSignInCommand(
                provider=_to_provider(provider), code=code, nonce=oauth_nonce
            )
        )
    except AuthError as error:
        return _redirect_to_failure(policy, error)
    response = RedirectResponse(policy.success_redirect_url, status_code=302)
    set_token_cookies(
        response,
        policy=policy,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )
    clear_sign_in_cookies(response, policy=policy)
    response.headers["Cache-Control"] = "no-store"
    return response
