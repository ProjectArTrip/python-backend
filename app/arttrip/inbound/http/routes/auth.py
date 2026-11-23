from fastapi import APIRouter, Depends, Request, Response

from arttrip.application.domain.auth.exceptions import AuthError
from arttrip.application.port.input.auth.commands import (
    ReissueTokensCommand,
    SignInCommand,
    SignOutCommand,
    SignOutWebCommand,
)
from arttrip.inbound.http.dependencies.auth import (
    CurrentUserDep,
    ReissueTokensUseCaseDep,
    SignInUseCaseDep,
    SignOutUseCaseDep,
    SignOutWebUseCaseDep,
)
from arttrip.inbound.http.dependencies.response import forbid_response_caching
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.schemas.auth import (
    RefreshTokenRequest,
    SignInRequest,
    SignInResponse,
    TokenPairResponse,
)
from arttrip.inbound.http.web_session import (
    ACCESS_TOKEN_COOKIE,
    REFRESH_TOKEN_COOKIE,
    WebSessionPolicyDep,
    clear_token_cookies,
    ensure_trusted_origin,
    set_token_cookies,
)

router = APIRouter()


@router.post(
    "/signIn",
    response_model=SignInResponse,
    dependencies=[Depends(forbid_response_caching)],
    responses=error_responses(
        AuthError.invalid_id_token,
        AuthError.provider_unavailable,
    ),
)
def sign_in(body: SignInRequest, use_case: SignInUseCaseDep) -> SignInResponse:
    result = use_case.sign_in(
        SignInCommand(provider=body.provider, id_token=body.id_token)
    )

    return SignInResponse(
        onboarding_step=result.onboarding_step,
        access_token=result.tokens.access_token,
        refresh_token=result.tokens.refresh_token,
    )


@router.post(
    "/reissue",
    response_model=TokenPairResponse,
    dependencies=[Depends(forbid_response_caching)],
    responses=error_responses(AuthError.invalid_refresh_token),
)
def reissue_tokens(
    body: RefreshTokenRequest, use_case: ReissueTokensUseCaseDep
) -> TokenPairResponse:
    tokens = use_case.reissue_tokens(
        ReissueTokensCommand(refresh_token=body.refresh_token)
    )
    return TokenPairResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.post(
    "/signOut",
    status_code=204,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def sign_out(
    body: RefreshTokenRequest,
    current_user: CurrentUserDep,
    use_case: SignOutUseCaseDep,
) -> None:
    use_case.sign_out(
        SignOutCommand(
            user_id=current_user.user_id,
            refresh_token=body.refresh_token,
            access_token_id=current_user.token_id,
            access_token_expires_at=current_user.token_expires_at,
        )
    )


@router.post(
    "/web/reissue",
    status_code=204,
    responses=error_responses(
        AuthError.untrusted_origin, AuthError.invalid_refresh_token
    ),
)
def reissue_web_tokens(
    request: Request,
    use_case: ReissueTokensUseCaseDep,
    policy: WebSessionPolicyDep,
) -> Response:
    ensure_trusted_origin(request, policy=policy)
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE)
    if refresh_token is None:
        raise AuthError.invalid_refresh_token()
    tokens = use_case.reissue_tokens(ReissueTokensCommand(refresh_token=refresh_token))
    response = Response(status_code=204)
    set_token_cookies(
        response,
        policy=policy,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@router.post(
    "/web/signOut",
    status_code=204,
    responses=error_responses(AuthError.untrusted_origin),
)
def sign_out_web(
    request: Request,
    use_case: SignOutWebUseCaseDep,
    policy: WebSessionPolicyDep,
) -> Response:
    ensure_trusted_origin(request, policy=policy)
    use_case.sign_out_web(
        SignOutWebCommand(
            refresh_token=request.cookies.get(REFRESH_TOKEN_COOKIE),
            access_token=request.cookies.get(ACCESS_TOKEN_COOKIE),
        )
    )
    response = Response(status_code=204)
    clear_token_cookies(response, policy=policy)
    response.headers["Cache-Control"] = "no-store"
    return response
