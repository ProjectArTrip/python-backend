from typing import Annotated

from fastapi import Depends

from arttrip.application.port.input.location.use_cases import (
    ListDomesticRegionsUseCase,
    ListOverseasCountriesUseCase,
)


def provide_list_overseas_countries_use_case() -> ListOverseasCountriesUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_list_domestic_regions_use_case() -> ListDomesticRegionsUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListOverseasCountriesUseCaseDep = Annotated[
    ListOverseasCountriesUseCase, Depends(provide_list_overseas_countries_use_case)
]
ListDomesticRegionsUseCaseDep = Annotated[
    ListDomesticRegionsUseCase, Depends(provide_list_domestic_regions_use_case)
]
