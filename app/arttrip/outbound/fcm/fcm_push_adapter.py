import logging
from collections.abc import Sequence
from typing import Final

from firebase_admin import App, exceptions, messaging

from arttrip.application.domain.notification.push_delivery_status import (
    PushDeliveryStatus,
)
from arttrip.application.port.output.push_sender_port import (
    PushMessage,
    PushOutcome,
    PushSenderPort,
    PushSendResult,
)

_logger = logging.getLogger(__name__)

MULTICAST_LIMIT: Final = 500

_STALE_TOKEN_ERRORS: Final = (
    messaging.UnregisteredError,
    messaging.SenderIdMismatchError,
    exceptions.InvalidArgumentError,
)


class FcmPushAdapter(PushSenderPort):
    def __init__(self, *, app: App) -> None:
        self._app = app

    def send(self, *, tokens: Sequence[str], message: PushMessage) -> PushSendResult:
        outcomes: list[PushOutcome] = []
        for start in range(0, len(tokens), MULTICAST_LIMIT):
            batch = list(tokens[start : start + MULTICAST_LIMIT])
            outcomes.extend(self._send_batch(batch, message))
        return PushSendResult(outcomes=tuple(outcomes))

    def _send_batch(self, batch: list[str], message: PushMessage) -> list[PushOutcome]:
        notification = messaging.Notification(title=message.title, body=message.body)
        data = dict(message.data)
        apns = _apns_config(message)

        multicast = messaging.MulticastMessage(
            tokens=batch,
            notification=notification,
            data=data,
            apns=apns,
        )

        try:
            response = messaging.send_each_for_multicast(multicast, app=self._app)
        except (exceptions.FirebaseError, ValueError) as error:
            _logger.warning("fcm push failed: %s", type(error).__name__)
            return [
                PushOutcome(
                    token=token,
                    status=PushDeliveryStatus.FAILED,
                    message_id=None,
                    error_code=type(error).__name__,
                )
                for token in batch
            ]
        _logger.info(
            "fcm push sent: success=%d failure=%d",
            response.success_count,
            response.failure_count,
        )

        outcomes = [
            _to_outcome(token, result)
            for token, result in zip(batch, response.responses, strict=True)
        ]

        for outcome in outcomes:
            _logger.debug(
                "fcm push outcome: token=%s status=%s message_id=%s error=%s",
                _mask(outcome.token),
                outcome.status,
                outcome.message_id,
                outcome.error_code,
            )
        return outcomes


def _to_outcome(token: str, result: messaging.SendResponse) -> PushOutcome:
    if result.success:
        return PushOutcome(
            token=token,
            status=PushDeliveryStatus.SENT,
            message_id=result.message_id,
            error_code=None,
        )
    error = result.exception
    status = (
        PushDeliveryStatus.STALE
        if isinstance(error, _STALE_TOKEN_ERRORS)
        else PushDeliveryStatus.FAILED
    )
    return PushOutcome(
        token=token,
        status=status,
        message_id=None,
        error_code=type(error).__name__ if error is not None else None,
    )


def _mask(token: str) -> str:
    if len(token) < 8:
        return "***"
    return f"{token[:4]}***{token[-4:]}"


def _apns_config(message: PushMessage) -> messaging.APNSConfig:
    return messaging.APNSConfig(
        headers={"apns-priority": "10", "apns-push-type": "alert"},
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                alert=messaging.ApsAlert(title=message.title, body=message.body),
                sound="default",
                badge=1,
            )
        ),
    )
