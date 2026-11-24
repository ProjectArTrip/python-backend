from fastapi import APIRouter, Depends, UploadFile, status

from arttrip.application.domain.image.exceptions import ImageError
from arttrip.application.domain.keyword.exceptions import KeywordError
from arttrip.application.domain.user.exceptions import UserError
from arttrip.application.port.input.user.commands import (
    ChangeNicknameCommand,
    ChangeProfileImageCommand,
    ChangePushEnabledCommand,
    DeleteAccountCommand,
    RegisterDeviceTokenCommand,
    ReplaceKeywordsCommand,
)
from arttrip.common import settings
from arttrip.inbound.http.dependencies.auth import (
    CurrentUserDep,
    DeleteAccountUseCaseDep,
)
from arttrip.inbound.http.dependencies.response import forbid_response_caching
from arttrip.inbound.http.dependencies.user import (
    ChangeNicknameUseCaseDep,
    ChangeProfileImageUseCaseDep,
    ChangePushEnabledUseCaseDep,
    GetProfileUseCaseDep,
    ListMyKeywordsUseCaseDep,
    RegisterDeviceTokenUseCaseDep,
    RemoveProfileImageUseCaseDep,
    ReplaceKeywordsUseCaseDep,
)
from arttrip.inbound.http.image_upload import read_image_upload
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.schemas.auth import RefreshTokenRequest
from arttrip.inbound.http.schemas.keywords import KeywordListResponse, KeywordResponse
from arttrip.inbound.http.schemas.users import (
    ChangeNicknameRequest,
    ChangeNicknameResponse,
    ChangePushEnabledRequest,
    ProfileImageResponse,
    PushEnabledResponse,
    RegisterDeviceTokenRequest,
    ReplaceKeywordsRequest,
    ReplaceKeywordsResponse,
    UserProfileResponse,
)

router = APIRouter()


@router.get(
    "/me",
    response_model=UserProfileResponse,
    dependencies=[Depends(forbid_response_caching)],
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def get_profile(
    current_user: CurrentUserDep,
    use_case: GetProfileUseCaseDep,
) -> UserProfileResponse:
    profile = use_case.get_profile(current_user.user_id)
    return UserProfileResponse(
        nickname=profile.nickname,
        email=profile.email,
        role=profile.role,
        onboarding_step=profile.onboarding_step,
        push_enabled=profile.push_enabled,
        profile_image_url=profile.profile_image_url,
    )


@router.patch(
    "/me",
    response_model=ChangeNicknameResponse,
    responses=error_responses(
        *AUTHENTICATION_ERRORS,
        UserError.invalid_nickname,
        UserError.duplicated_nickname,
    ),
)
def change_nickname(
    body: ChangeNicknameRequest,
    current_user: CurrentUserDep,
    use_case: ChangeNicknameUseCaseDep,
) -> ChangeNicknameResponse:
    result = use_case.change_nickname(
        ChangeNicknameCommand(user_id=current_user.user_id, nickname=body.nickname)
    )
    return ChangeNicknameResponse(
        nickname=result.nickname, onboarding_step=result.onboarding_step
    )


@router.patch(
    "/me/image",
    response_model=ProfileImageResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS, ImageError.storage_unavailable),
)
def change_profile_image(
    image: UploadFile,
    current_user: CurrentUserDep,
    use_case: ChangeProfileImageUseCaseDep,
) -> ProfileImageResponse:
    limits = settings.image
    prepared = read_image_upload(
        image,
        max_bytes=limits.max_bytes,
        max_pixels=limits.max_pixels,
        max_side=limits.max_side,
        quality=limits.jpeg_quality,
    )
    result = use_case.change_profile_image(
        ChangeProfileImageCommand(
            user_id=current_user.user_id,
            content=prepared.content,
            content_type=prepared.content_type,
            extension=prepared.extension,
        )
    )
    return ProfileImageResponse(profile_image_url=result.url)


@router.delete(
    "/me/image",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def remove_profile_image(
    current_user: CurrentUserDep,
    use_case: RemoveProfileImageUseCaseDep,
) -> None:
    use_case.remove_profile_image(current_user.user_id)


@router.put(
    "/me/keywords",
    response_model=ReplaceKeywordsResponse,
    responses=error_responses(
        *AUTHENTICATION_ERRORS,
        KeywordError.not_found,
        UserError.genre_keyword_required,
        UserError.keyword_step_not_reached,
    ),
)
def replace_keywords(
    body: ReplaceKeywordsRequest,
    current_user: CurrentUserDep,
    use_case: ReplaceKeywordsUseCaseDep,
) -> ReplaceKeywordsResponse:
    result = use_case.replace_keywords(
        ReplaceKeywordsCommand(
            user_id=current_user.user_id, keyword_ids=tuple(body.keyword_ids)
        )
    )
    return ReplaceKeywordsResponse(
        keyword_ids=list(result.keyword_ids), onboarding_step=result.onboarding_step
    )


@router.put(
    "/me/pushEnabled",
    response_model=PushEnabledResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def change_push_enabled(
    body: ChangePushEnabledRequest,
    current_user: CurrentUserDep,
    use_case: ChangePushEnabledUseCaseDep,
) -> PushEnabledResponse:
    push_enabled = use_case.change_push_enabled(
        ChangePushEnabledCommand(user_id=current_user.user_id, enabled=body.enabled)
    )
    return PushEnabledResponse(push_enabled=push_enabled)


@router.put(
    "/me/deviceToken",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def register_device_token(
    body: RegisterDeviceTokenRequest,
    current_user: CurrentUserDep,
    use_case: RegisterDeviceTokenUseCaseDep,
) -> None:
    use_case.register_device_token(
        RegisterDeviceTokenCommand(user_id=current_user.user_id, token=body.token)
    )


@router.get(
    "/me/keywords",
    response_model=KeywordListResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def list_my_keywords(
    current_user: CurrentUserDep,
    use_case: ListMyKeywordsUseCaseDep,
) -> KeywordListResponse:
    keywords = use_case.list_my_keywords(current_user.user_id)
    return KeywordListResponse(
        keywords=[
            KeywordResponse(
                keyword_id=keyword.keyword_id,
                name=keyword.name,
                type=keyword.keyword_type,
            )
            for keyword in keywords
        ]
    )


@router.post(
    "/me/delete-account",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(
        *AUTHENTICATION_ERRORS, UserError.admin_cannot_delete_account
    ),
)
def delete_account(
    body: RefreshTokenRequest,
    current_user: CurrentUserDep,
    use_case: DeleteAccountUseCaseDep,
) -> None:
    use_case.delete_account(
        DeleteAccountCommand(
            user_id=current_user.user_id,
            refresh_token=body.refresh_token,
            access_token_id=current_user.token_id,
            access_token_expires_at=current_user.token_expires_at,
        )
    )
