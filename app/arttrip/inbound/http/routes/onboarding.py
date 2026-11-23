from fastapi import APIRouter

from arttrip.application.domain.keyword.exceptions import KeywordError
from arttrip.application.domain.user.exceptions import UserError
from arttrip.application.port.input.user.commands import (
    CompleteOnboardingKeywordsCommand,
    CompleteOnboardingNicknameCommand,
    SelectOnboardingRoleCommand,
)
from arttrip.inbound.http.dependencies.auth import CurrentUserDep
from arttrip.inbound.http.dependencies.user import (
    CompleteOnboardingKeywordsUseCaseDep,
    CompleteOnboardingNicknameUseCaseDep,
    SelectOnboardingRoleUseCaseDep,
)
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.schemas.onboarding import (
    CompleteOnboardingKeywordsRequest,
    CompleteOnboardingNicknameRequest,
    OnboardingProgressResponse,
    SelectOnboardingRoleRequest,
)
from arttrip.inbound.http.schemas.users import (
    ChangeNicknameResponse,
    ReplaceKeywordsResponse,
)

router = APIRouter()


@router.post(
    "/role",
    response_model=OnboardingProgressResponse,
    responses=error_responses(
        *AUTHENTICATION_ERRORS,
        UserError.role_already_selected,
        UserError.role_not_selectable,
        UserError.role_step_not_reached,
    ),
)
def select_onboarding_role(
    body: SelectOnboardingRoleRequest,
    current_user: CurrentUserDep,
    use_case: SelectOnboardingRoleUseCaseDep,
) -> OnboardingProgressResponse:

    progress = use_case.select_onboarding_role(
        SelectOnboardingRoleCommand(
            user_id=current_user.user_id,
            desired_role=body.role,
        )
    )

    return OnboardingProgressResponse(
        onboarding_step=progress.onboarding_step, role=progress.role
    )


@router.post(
    "/nickname",
    response_model=ChangeNicknameResponse,
    responses=error_responses(
        *AUTHENTICATION_ERRORS,
        UserError.invalid_nickname,
        UserError.duplicated_nickname,
        UserError.nickname_step_already_completed,
    ),
)
def complete_onboarding_nickname(
    body: CompleteOnboardingNicknameRequest,
    current_user: CurrentUserDep,
    use_case: CompleteOnboardingNicknameUseCaseDep,
) -> ChangeNicknameResponse:
    result = use_case.complete_onboarding_nickname(
        CompleteOnboardingNicknameCommand(
            user_id=current_user.user_id, nickname=body.nickname
        )
    )
    return ChangeNicknameResponse(
        nickname=result.nickname, onboarding_step=result.onboarding_step
    )


@router.post(
    "/keywords",
    response_model=ReplaceKeywordsResponse,
    responses=error_responses(
        *AUTHENTICATION_ERRORS,
        KeywordError.not_found,
        UserError.genre_keyword_required,
        UserError.keyword_step_not_reached,
        UserError.keyword_step_already_completed,
    ),
)
def complete_onboarding_keywords(
    body: CompleteOnboardingKeywordsRequest,
    current_user: CurrentUserDep,
    use_case: CompleteOnboardingKeywordsUseCaseDep,
) -> ReplaceKeywordsResponse:
    result = use_case.complete_onboarding_keywords(
        CompleteOnboardingKeywordsCommand(
            user_id=current_user.user_id, keyword_ids=tuple(body.keyword_ids)
        )
    )
    return ReplaceKeywordsResponse(
        keyword_ids=list(result.keyword_ids), onboarding_step=result.onboarding_step
    )
