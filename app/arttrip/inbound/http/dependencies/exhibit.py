from typing import Annotated

from fastapi import Depends

from arttrip.application.port.input.exhibit.use_cases import (
    CreateExhibitUseCase,
    DeleteArtistExhibitUseCase,
    DeleteExhibitUseCase,
    FetchOpenDataExhibitsUseCase,
    GetExhibitImportGuideUseCase,
    GetExhibitUseCase,
    GetManagedExhibitUseCase,
    ImportExhibitsUseCase,
    ListArtistExhibitsUseCase,
    ListExhibitsUseCase,
    ListRecentExhibitsUseCase,
    PreviewExhibitImportUseCase,
    RegisterArtistExhibitUseCase,
    SearchExhibitsUseCase,
    UpdateArtistExhibitUseCase,
    UpdateExhibitUseCase,
)


def provide_get_exhibit_use_case() -> GetExhibitUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_list_exhibits_use_case() -> ListExhibitsUseCase:
    raise NotImplementedError("composition root must override this dependency")


GetExhibitUseCaseDep = Annotated[
    GetExhibitUseCase, Depends(provide_get_exhibit_use_case)
]


ListExhibitsUseCaseDep = Annotated[
    ListExhibitsUseCase, Depends(provide_list_exhibits_use_case)
]


def provide_list_recent_exhibits_use_case() -> ListRecentExhibitsUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListRecentExhibitsUseCaseDep = Annotated[
    ListRecentExhibitsUseCase, Depends(provide_list_recent_exhibits_use_case)
]


def provide_search_exhibits_use_case() -> SearchExhibitsUseCase:
    raise NotImplementedError("composition root must override this dependency")


SearchExhibitsUseCaseDep = Annotated[
    SearchExhibitsUseCase, Depends(provide_search_exhibits_use_case)
]


def provide_get_managed_exhibit_use_case() -> GetManagedExhibitUseCase:
    raise NotImplementedError("composition root must override this dependency")


GetManagedExhibitUseCaseDep = Annotated[
    GetManagedExhibitUseCase, Depends(provide_get_managed_exhibit_use_case)
]


def provide_update_exhibit_use_case() -> UpdateExhibitUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_delete_exhibit_use_case() -> DeleteExhibitUseCase:
    raise NotImplementedError("composition root must override this dependency")


UpdateExhibitUseCaseDep = Annotated[
    UpdateExhibitUseCase, Depends(provide_update_exhibit_use_case)
]
DeleteExhibitUseCaseDep = Annotated[
    DeleteExhibitUseCase, Depends(provide_delete_exhibit_use_case)
]


def provide_create_exhibit_use_case() -> CreateExhibitUseCase:
    raise NotImplementedError("composition root must override this dependency")


CreateExhibitUseCaseDep = Annotated[
    CreateExhibitUseCase, Depends(provide_create_exhibit_use_case)
]


def provide_get_exhibit_import_guide_use_case() -> GetExhibitImportGuideUseCase:
    raise NotImplementedError("composition root must override this dependency")


GetExhibitImportGuideUseCaseDep = Annotated[
    GetExhibitImportGuideUseCase, Depends(provide_get_exhibit_import_guide_use_case)
]


def provide_preview_exhibit_import_use_case() -> PreviewExhibitImportUseCase:
    raise NotImplementedError("composition root must override this dependency")


PreviewExhibitImportUseCaseDep = Annotated[
    PreviewExhibitImportUseCase, Depends(provide_preview_exhibit_import_use_case)
]


def provide_import_exhibits_use_case() -> ImportExhibitsUseCase:
    raise NotImplementedError("composition root must override this dependency")


ImportExhibitsUseCaseDep = Annotated[
    ImportExhibitsUseCase, Depends(provide_import_exhibits_use_case)
]


def provide_register_artist_exhibit_use_case() -> RegisterArtistExhibitUseCase:
    raise NotImplementedError("composition root must override this dependency")


RegisterArtistExhibitUseCaseDep = Annotated[
    RegisterArtistExhibitUseCase, Depends(provide_register_artist_exhibit_use_case)
]


def provide_list_artist_exhibits_use_case() -> ListArtistExhibitsUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListArtistExhibitsUseCaseDep = Annotated[
    ListArtistExhibitsUseCase, Depends(provide_list_artist_exhibits_use_case)
]


def provide_update_artist_exhibit_use_case() -> UpdateArtistExhibitUseCase:
    raise NotImplementedError("composition root must override this dependency")


UpdateArtistExhibitUseCaseDep = Annotated[
    UpdateArtistExhibitUseCase, Depends(provide_update_artist_exhibit_use_case)
]


def provide_delete_artist_exhibit_use_case() -> DeleteArtistExhibitUseCase:
    raise NotImplementedError("composition root must override this dependency")


DeleteArtistExhibitUseCaseDep = Annotated[
    DeleteArtistExhibitUseCase, Depends(provide_delete_artist_exhibit_use_case)
]


def provide_fetch_open_data_exhibits_use_case() -> FetchOpenDataExhibitsUseCase:
    raise NotImplementedError("composition root must override this dependency")


FetchOpenDataExhibitsUseCaseDep = Annotated[
    FetchOpenDataExhibitsUseCase, Depends(provide_fetch_open_data_exhibits_use_case)
]
