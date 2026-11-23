from fastapi import Request

from arttrip.application.domain.auth.auth_services import (
    AuthenticateService,
    CompleteWebSignInService,
    ReissueTokensService,
    SignInService,
    SignOutService,
    SignOutWebService,
    StartWebSignInService,
)
from arttrip.application.domain.user.user_services import DeleteAccountService
from arttrip.application.port.input.auth.use_cases import (
    AuthenticateUseCase,
    CompleteWebSignInUseCase,
    ReissueTokensUseCase,
    SignInUseCase,
    SignOutUseCase,
    SignOutWebUseCase,
    StartWebSignInUseCase,
)
from arttrip.application.port.input.user.use_cases import DeleteAccountUseCase
from arttrip.bootstrap.wiring.common import Overrides, new_unit_of_work
from arttrip.inbound.http.dependencies.auth import (
    provide_authenticate_use_case,
    provide_complete_web_sign_in_use_case,
    provide_delete_account_use_case,
    provide_reissue_tokens_use_case,
    provide_sign_in_use_case,
    provide_sign_out_use_case,
    provide_sign_out_web_use_case,
    provide_start_web_sign_in_use_case,
)


def build_authenticate_use_case(request: Request) -> AuthenticateUseCase:
    return AuthenticateService(
        tokens=request.app.state.token,
        access_token_denylist=request.app.state.access_token_denylist,
    )


def build_sign_in_use_case(request: Request) -> SignInUseCase:
    return SignInService(
        oauth=request.app.state.oauth,
        uow=new_unit_of_work(request),
        tokens=request.app.state.token,
        refresh_tokens=request.app.state.refresh_tokens,
        image_policy=request.app.state.profile_image_policy,
    )


def build_reissue_tokens_use_case(request: Request) -> ReissueTokensUseCase:
    return ReissueTokensService(
        uow=new_unit_of_work(request),
        tokens=request.app.state.token,
        refresh_tokens=request.app.state.refresh_tokens,
    )


def build_sign_out_use_case(request: Request) -> SignOutUseCase:
    return SignOutService(
        uow=new_unit_of_work(request),
        refresh_tokens=request.app.state.refresh_tokens,
        access_token_denylist=request.app.state.access_token_denylist,
    )


def build_delete_account_use_case(request: Request) -> DeleteAccountUseCase:
    return DeleteAccountService(
        uow=new_unit_of_work(request),
        refresh_tokens=request.app.state.refresh_tokens,
        access_token_denylist=request.app.state.access_token_denylist,
    )


def build_start_web_sign_in_use_case(request: Request) -> StartWebSignInUseCase:
    return StartWebSignInService(web_oauth=request.app.state.web_oauth)


def build_complete_web_sign_in_use_case(request: Request) -> CompleteWebSignInUseCase:
    return CompleteWebSignInService(
        web_oauth=request.app.state.web_oauth,
        oauth=request.app.state.oauth,
        uow=new_unit_of_work(request),
        tokens=request.app.state.token,
        refresh_tokens=request.app.state.refresh_tokens,
    )


def build_sign_out_web_use_case(request: Request) -> SignOutWebUseCase:
    return SignOutWebService(
        tokens=request.app.state.token,
        refresh_tokens=request.app.state.refresh_tokens,
        access_token_denylist=request.app.state.access_token_denylist,
    )


def wire_auth(overrides: Overrides) -> None:
    overrides[provide_authenticate_use_case] = build_authenticate_use_case
    overrides[provide_sign_in_use_case] = build_sign_in_use_case
    overrides[provide_reissue_tokens_use_case] = build_reissue_tokens_use_case
    overrides[provide_sign_out_use_case] = build_sign_out_use_case
    overrides[provide_delete_account_use_case] = build_delete_account_use_case
    overrides[provide_start_web_sign_in_use_case] = build_start_web_sign_in_use_case
    overrides[provide_complete_web_sign_in_use_case] = (
        build_complete_web_sign_in_use_case
    )
    overrides[provide_sign_out_web_use_case] = build_sign_out_web_use_case
