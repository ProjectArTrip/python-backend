from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from arttrip.application.domain.auth.exceptions import AuthError
from arttrip.application.domain.user.role import UserRole
from arttrip.application.port.input.auth.results import AuthenticatedUser
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
from arttrip.inbound.http.web_session import (
    ACCESS_TOKEN_COOKIE,
    WebSessionPolicyDep,
    ensure_trusted_origin,
)

bearer_scheme = HTTPBearer(auto_error=False)


def provide_authenticate_use_case() -> AuthenticateUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_sign_in_use_case() -> SignInUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_reissue_tokens_use_case() -> ReissueTokensUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_sign_out_use_case() -> SignOutUseCase:
    raise NotImplementedError("composition root must override this dependency")


AuthenticateUseCaseDep = Annotated[
    AuthenticateUseCase, Depends(provide_authenticate_use_case)
]


SignInUseCaseDep = Annotated[SignInUseCase, Depends(provide_sign_in_use_case)]


ReissueTokensUseCaseDep = Annotated[
    ReissueTokensUseCase, Depends(provide_reissue_tokens_use_case)
]


SignOutUseCaseDep = Annotated[SignOutUseCase, Depends(provide_sign_out_use_case)]


def provide_delete_account_use_case() -> DeleteAccountUseCase:
    raise NotImplementedError("composition root must override this dependency")


DeleteAccountUseCaseDep = Annotated[
    DeleteAccountUseCase, Depends(provide_delete_account_use_case)
]


def provide_start_web_sign_in_use_case() -> StartWebSignInUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_complete_web_sign_in_use_case() -> CompleteWebSignInUseCase:
    raise NotImplementedError("composition root must override this dependency")


StartWebSignInUseCaseDep = Annotated[
    StartWebSignInUseCase, Depends(provide_start_web_sign_in_use_case)
]
CompleteWebSignInUseCaseDep = Annotated[
    CompleteWebSignInUseCase, Depends(provide_complete_web_sign_in_use_case)
]


def provide_sign_out_web_use_case() -> SignOutWebUseCase:
    raise NotImplementedError("composition root must override this dependency")


SignOutWebUseCaseDep = Annotated[
    SignOutWebUseCase, Depends(provide_sign_out_web_use_case)
]


def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    use_case: AuthenticateUseCaseDep,
    policy: WebSessionPolicyDep,
) -> AuthenticatedUser:
    if credentials is not None:
        return use_case.authenticate(credentials.credentials)
    cookie_token = request.cookies.get(ACCESS_TOKEN_COOKIE)
    if cookie_token is not None:
        ensure_trusted_origin(request, policy=policy)
    return use_case.authenticate(cookie_token)


CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]


def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    use_case: AuthenticateUseCaseDep,
) -> AuthenticatedUser | None:
    if credentials is None:
        return None
    return use_case.authenticate(credentials.credentials)


OptionalUserDep = Annotated[AuthenticatedUser | None, Depends(get_optional_user)]


def require_admin(current_user: CurrentUserDep) -> AuthenticatedUser:
    if current_user.role is not UserRole.ADMIN:
        raise AuthError.permission_denied()
    return current_user


AdminUserDep = Annotated[AuthenticatedUser, Depends(require_admin)]
