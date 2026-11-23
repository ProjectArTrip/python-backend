import secrets
from datetime import UTC, datetime

from arttrip.application.domain.auth.exceptions import AuthError
from arttrip.application.domain.auth.social_provider import SocialProvider
from arttrip.application.domain.auth.token_pair import issue_token_pair
from arttrip.application.domain.user.profile_image_policy import ProfileImagePolicy
from arttrip.application.domain.user.user import User
from arttrip.application.port.input.auth.commands import (
    CompleteWebSignInCommand,
    ReissueTokensCommand,
    SignInCommand,
    SignOutCommand,
    SignOutWebCommand,
)
from arttrip.application.port.input.auth.results import (
    AuthenticatedUser,
    SignInResult,
    TokenPair,
    WebSignInStart,
)
from arttrip.application.port.input.auth.use_cases import (
    AuthenticateUseCase,
    CompleteWebSignInUseCase,
    ReissueTokensUseCase,
    SignInUseCase,
    SignOutUseCase,
    SignOutWebUseCase,
    StartWebSignInUseCase,
)
from arttrip.application.port.output.access_token_denylist_port import (
    AccessTokenDenylistPort,
)
from arttrip.application.port.output.oauth_port import OAuthPort
from arttrip.application.port.output.refresh_token_port import RefreshTokenPort
from arttrip.application.port.output.token_port import TokenPort
from arttrip.application.port.output.unit_of_work import UnitOfWork
from arttrip.application.port.output.web_oauth_port import WebOAuthPort


class AuthenticateService(AuthenticateUseCase):
    def __init__(
        self,
        *,
        tokens: TokenPort,
        access_token_denylist: AccessTokenDenylistPort,
    ) -> None:
        self._tokens = tokens
        self._access_token_denylist = access_token_denylist

    def authenticate(self, access_token: str | None) -> AuthenticatedUser:
        if access_token is None:
            raise AuthError.missing_access_token()

        claims = self._tokens.verify_access_token(access_token)

        if self._access_token_denylist.is_denied(claims.token_id):
            raise AuthError.invalid_access_token()

        return AuthenticatedUser(
            user_id=claims.user_id,
            role=claims.role,
            token_id=claims.token_id,
            token_expires_at=claims.expires_at,
        )


class SignInService(SignInUseCase):
    def __init__(
        self,
        *,
        oauth: OAuthPort,
        uow: UnitOfWork,
        tokens: TokenPort,
        refresh_tokens: RefreshTokenPort,
        image_policy: ProfileImagePolicy,
    ) -> None:
        self._oauth = oauth
        self._uow = uow
        self._tokens = tokens
        self._refresh_tokens = refresh_tokens
        self._image_policy = image_policy

    def sign_in(self, command: SignInCommand) -> SignInResult:
        identity = self._oauth.verify(
            provider=command.provider, id_token=command.id_token
        )
        now = datetime.now(UTC)

        with self._uow as uow:
            linked = uow.users.find_by_social_identity(
                provider=identity.provider, provider_user_id=identity.subject
            )

            if linked is not None:
                user = linked
            else:
                user = User.register(
                    provider_name=None,
                    email=identity.email,
                    now=now,
                    image_policy=self._image_policy,
                )
                user.link_social(
                    provider=identity.provider,
                    provider_user_id=identity.subject,
                    now=now,
                )
                uow.users.add(user)

            user_id = user.id
            role = user.role
            onboarding_step = user.onboarding_step

        if user_id is None:
            raise RuntimeError("user must be persisted before issuing a token")

        return SignInResult(
            tokens=issue_token_pair(
                tokens=self._tokens,
                refresh_tokens=self._refresh_tokens,
                user_id=user_id,
                role=role,
                now=now,
            ),
            onboarding_step=onboarding_step,
        )


class ReissueTokensService(ReissueTokensUseCase):
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        tokens: TokenPort,
        refresh_tokens: RefreshTokenPort,
    ) -> None:
        self._uow = uow
        self._tokens = tokens
        self._refresh_tokens = refresh_tokens

    def reissue_tokens(self, command: ReissueTokensCommand) -> TokenPair:
        user_id = self._refresh_tokens.consume(command.refresh_token)
        if user_id is None:
            raise AuthError.invalid_refresh_token()

        with self._uow as uow:
            user = uow.users.find_by_id(user_id)
            if user is None:
                raise AuthError.invalid_refresh_token()
            role = user.role

        return issue_token_pair(
            tokens=self._tokens,
            refresh_tokens=self._refresh_tokens,
            user_id=user_id,
            role=role,
            now=datetime.now(UTC),
        )


class SignOutService(SignOutUseCase):
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        refresh_tokens: RefreshTokenPort,
        access_token_denylist: AccessTokenDenylistPort,
    ) -> None:
        self._uow = uow
        self._refresh_tokens = refresh_tokens
        self._access_token_denylist = access_token_denylist

    def sign_out(self, command: SignOutCommand) -> None:
        self._refresh_tokens.consume(command.refresh_token)
        self._access_token_denylist.deny(
            token_id=command.access_token_id,
            expires_at=command.access_token_expires_at,
        )
        with self._uow as uow:
            uow.device_tokens.clear_for_user(command.user_id)


class StartWebSignInService(StartWebSignInUseCase):
    def __init__(self, *, web_oauth: WebOAuthPort) -> None:
        self._web_oauth = web_oauth

    def start_web_sign_in(self, provider: SocialProvider) -> WebSignInStart:
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        return WebSignInStart(
            authorization_url=self._web_oauth.build_authorization_url(
                provider=provider, state=state, nonce=nonce
            ),
            state=state,
            nonce=nonce,
        )


class CompleteWebSignInService(CompleteWebSignInUseCase):
    def __init__(
        self,
        *,
        web_oauth: WebOAuthPort,
        oauth: OAuthPort,
        uow: UnitOfWork,
        tokens: TokenPort,
        refresh_tokens: RefreshTokenPort,
    ) -> None:
        self._web_oauth = web_oauth
        self._oauth = oauth
        self._uow = uow
        self._tokens = tokens
        self._refresh_tokens = refresh_tokens

    def complete_web_sign_in(self, command: CompleteWebSignInCommand) -> TokenPair:
        id_token = self._web_oauth.exchange_code(
            provider=command.provider, code=command.code
        )
        identity = self._oauth.verify(provider=command.provider, id_token=id_token)
        if identity.nonce is None or not secrets.compare_digest(
            identity.nonce.encode(), command.nonce.encode()
        ):
            raise AuthError.invalid_id_token()
        with self._uow as uow:
            user = uow.users.find_by_social_identity(
                provider=identity.provider, provider_user_id=identity.subject
            )
            if user is None:
                raise AuthError.web_sign_in_not_allowed()
            user.ensure_can_sign_in_web()
            user_id = user.id
            role = user.role
        if user_id is None:
            raise RuntimeError("user must be persisted before issuing a token")
        return issue_token_pair(
            tokens=self._tokens,
            refresh_tokens=self._refresh_tokens,
            user_id=user_id,
            role=role,
            now=datetime.now(UTC),
        )


class SignOutWebService(SignOutWebUseCase):
    def __init__(
        self,
        *,
        tokens: TokenPort,
        refresh_tokens: RefreshTokenPort,
        access_token_denylist: AccessTokenDenylistPort,
    ) -> None:
        self._tokens = tokens
        self._refresh_tokens = refresh_tokens
        self._access_token_denylist = access_token_denylist

    def sign_out_web(self, command: SignOutWebCommand) -> None:
        if command.refresh_token is not None:
            self._refresh_tokens.consume(command.refresh_token)
        if command.access_token is None:
            return
        try:
            claims = self._tokens.verify_access_token(command.access_token)
        except AuthError:
            return
        self._access_token_denylist.deny(
            token_id=claims.token_id, expires_at=claims.expires_at
        )
