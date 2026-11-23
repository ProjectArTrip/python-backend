from typing import Annotated

from fastapi import Depends

from arttrip.application.port.input.artist_application.use_cases import (
    ApproveArtistApplicationUseCase,
    GetLatestArtistApplicationUseCase,
    GetManagedArtistApplicationUseCase,
    ListArtistApplicationsUseCase,
    RejectArtistApplicationUseCase,
    SubmitArtistApplicationUseCase,
)


def provide_submit_artist_application_use_case() -> SubmitArtistApplicationUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_get_latest_artist_application_use_case() -> (
    GetLatestArtistApplicationUseCase
):
    raise NotImplementedError("composition root must override this dependency")


def provide_list_artist_applications_use_case() -> ListArtistApplicationsUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_approve_artist_application_use_case() -> ApproveArtistApplicationUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_reject_artist_application_use_case() -> RejectArtistApplicationUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_get_managed_artist_application_use_case() -> (
    GetManagedArtistApplicationUseCase
):
    raise NotImplementedError("composition root must override this dependency")


SubmitArtistApplicationUseCaseDep = Annotated[
    SubmitArtistApplicationUseCase, Depends(provide_submit_artist_application_use_case)
]


GetLatestArtistApplicationUseCaseDep = Annotated[
    GetLatestArtistApplicationUseCase,
    Depends(provide_get_latest_artist_application_use_case),
]


ListArtistApplicationsUseCaseDep = Annotated[
    ListArtistApplicationsUseCase, Depends(provide_list_artist_applications_use_case)
]


ApproveArtistApplicationUseCaseDep = Annotated[
    ApproveArtistApplicationUseCase,
    Depends(provide_approve_artist_application_use_case),
]


RejectArtistApplicationUseCaseDep = Annotated[
    RejectArtistApplicationUseCase, Depends(provide_reject_artist_application_use_case)
]

GetManagedArtistApplicationUseCaseDep = Annotated[
    GetManagedArtistApplicationUseCase,
    Depends(provide_get_managed_artist_application_use_case),
]
