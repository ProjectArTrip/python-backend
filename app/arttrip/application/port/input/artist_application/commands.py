from dataclasses import dataclass


@dataclass(frozen=True)
class SubmitArtistApplicationCommand:
    user_id: int
    introduction: str
    portfolio_url: str | None


@dataclass(frozen=True)
class ApproveArtistApplicationCommand:
    application_id: int
    reviewer_id: int


@dataclass(frozen=True)
class RejectArtistApplicationCommand:
    application_id: int
    reviewer_id: int
    reason: str
