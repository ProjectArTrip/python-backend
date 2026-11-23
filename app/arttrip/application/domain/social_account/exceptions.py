from arttrip.application.util.exception import DomainException


class SocialAccountError(DomainException):
    @classmethod
    def blank_provider_user_id(cls) -> "SocialAccountError":
        return cls(
            code="SOCIAL_ACCOUNT_PROVIDER_USER_ID_BLANK",
            message="provider_user_id must not be blank",
        )
