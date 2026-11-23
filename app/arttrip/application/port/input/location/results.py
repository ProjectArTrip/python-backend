from dataclasses import dataclass


@dataclass(frozen=True)
class CountryView:
    code: str
    name: str


@dataclass(frozen=True)
class RegionView:
    name: str
    image_url: str | None
