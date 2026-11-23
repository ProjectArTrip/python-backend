from typing import Annotated

from fastapi import Depends

from arttrip.application.port.input.curation.use_cases import (
    CreateCurationUseCase,
    DeleteCurationUseCase,
    GetCurationUseCase,
    GetManagedCurationUseCase,
    PickCurationUseCase,
    SearchCurationsUseCase,
    UpdateCurationUseCase,
)


def provide_get_curation_use_case() -> GetCurationUseCase:
    raise NotImplementedError("composition root must override this dependency")


GetCurationUseCaseDep = Annotated[
    GetCurationUseCase, Depends(provide_get_curation_use_case)
]


def provide_pick_curation_use_case() -> PickCurationUseCase:
    raise NotImplementedError("composition root must override this dependency")


PickCurationUseCaseDep = Annotated[
    PickCurationUseCase, Depends(provide_pick_curation_use_case)
]


def provide_search_curations_use_case() -> SearchCurationsUseCase:
    raise NotImplementedError("composition root must override this dependency")


SearchCurationsUseCaseDep = Annotated[
    SearchCurationsUseCase, Depends(provide_search_curations_use_case)
]


def provide_get_managed_curation_use_case() -> GetManagedCurationUseCase:
    raise NotImplementedError("composition root must override this dependency")


GetManagedCurationUseCaseDep = Annotated[
    GetManagedCurationUseCase, Depends(provide_get_managed_curation_use_case)
]


def provide_create_curation_use_case() -> CreateCurationUseCase:
    raise NotImplementedError("composition root must override this dependency")


CreateCurationUseCaseDep = Annotated[
    CreateCurationUseCase, Depends(provide_create_curation_use_case)
]


def provide_update_curation_use_case() -> UpdateCurationUseCase:
    raise NotImplementedError("composition root must override this dependency")


UpdateCurationUseCaseDep = Annotated[
    UpdateCurationUseCase, Depends(provide_update_curation_use_case)
]


def provide_delete_curation_use_case() -> DeleteCurationUseCase:
    raise NotImplementedError("composition root must override this dependency")


DeleteCurationUseCaseDep = Annotated[
    DeleteCurationUseCase, Depends(provide_delete_curation_use_case)
]
