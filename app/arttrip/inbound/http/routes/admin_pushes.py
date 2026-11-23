from typing import Annotated

from fastapi import APIRouter, Path

from arttrip.application.port.input.notification.commands import SendPushCommand
from arttrip.application.port.input.notification.results import PushDispatchResult
from arttrip.inbound.http.dependencies.notification import SendPushUseCaseDep
from arttrip.inbound.http.openapi import ADMIN_ERRORS, error_responses
from arttrip.inbound.http.schemas.admin_pushes import (
    BulkPushRequest,
    BurstPushRequest,
    PushDispatchResponse,
    PushMessageRequest,
)

router = APIRouter()

UserIdParam = Annotated[int, Path(gt=0)]


@router.post(
    "/users/{user_id}",
    response_model=PushDispatchResponse,
    responses=error_responses(*ADMIN_ERRORS),
)
def send_push_to_user(
    user_id: UserIdParam,
    body: PushMessageRequest,
    use_case: SendPushUseCaseDep,
) -> PushDispatchResponse:
    result = use_case.send_push(
        SendPushCommand(
            user_ids=(user_id,),
            title=body.title,
            body=body.body,
            data=body.to_data(),
        )
    )
    return _to_response(result)


@router.post(
    "",
    response_model=PushDispatchResponse,
    responses=error_responses(*ADMIN_ERRORS),
)
def send_push_to_users(
    body: BulkPushRequest,
    use_case: SendPushUseCaseDep,
) -> PushDispatchResponse:

    result = use_case.send_push(
        SendPushCommand(
            user_ids=tuple(dict.fromkeys(body.user_ids)),
            title=body.title,
            body=body.body,
            data=body.to_data(),
        )
    )
    return _to_response(result)


@router.post(
    "/users/{user_id}/burst",
    response_model=PushDispatchResponse,
    responses=error_responses(*ADMIN_ERRORS),
)
def send_burst_to_user(
    user_id: UserIdParam,
    body: BurstPushRequest,
    use_case: SendPushUseCaseDep,
) -> PushDispatchResponse:

    result = use_case.send_push(
        SendPushCommand(
            user_ids=(user_id,),
            title=body.title,
            body=body.body,
            data=body.to_data(),
            repeat=body.count,
        )
    )
    return _to_response(result)


def _to_response(result: PushDispatchResult) -> PushDispatchResponse:
    return PushDispatchResponse(
        dispatch_id=result.dispatch_id,
        requested_users=result.requested_users,
        targeted_tokens=result.targeted_tokens,
        succeeded=result.succeeded,
        failed=result.failed,
        removed_tokens=result.removed_tokens,
    )
