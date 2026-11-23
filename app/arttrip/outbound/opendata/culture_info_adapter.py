import logging
from datetime import datetime
from html import unescape
from typing import Final
from xml.etree.ElementTree import Element

import httpx
from defusedxml.common import DefusedXmlException
from defusedxml.ElementTree import ParseError, fromstring

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.port.output.exhibit_source_port import (
    ExhibitSourcePort,
    SourcedExhibit,
    SourcedExhibitPage,
)

_logger = logging.getLogger(__name__)

EXHIBIT_REALM_CODE: Final = "D000"
SUCCESS_RESULT_CODE: Final = "00"
SOURCE_DATE_FORMAT: Final = "%Y%m%d"
DOMESTIC_COUNTRY_NAME: Final = "한국"
REGION_BY_AREA: Final = {
    "서울": "서울",
    "경기": "경기",
    "충북": "충청",
    "충남": "충청",
    "대전": "충청",
    "세종": "충청",
    "강원": "강원",
    "전북": "전라",
    "전남": "전라",
    "광주": "전라",
    "경북": "경상",
    "경남": "경상",
    "부산": "경상",
    "대구": "경상",
    "울산": "경상",
    "제주": "제주",
}


class CultureInfoExhibitSourceAdapter(ExhibitSourcePort):
    def __init__(
        self,
        *,
        http_client: httpx.Client,
        base_url: str,
        service_key: str,
        excluded_areas: frozenset[str],
    ) -> None:
        self._http_client = http_client
        self._base_url = base_url
        self._service_key = service_key
        self._excluded_areas = excluded_areas

    def fetch_page(self, *, page_no: int, size: int) -> SourcedExhibitPage:
        body = self._get(
            "/realm2",
            {"PageNo": page_no, "numOfrows": size, "realmCode": EXHIBIT_REALM_CODE},
        )
        items: list[SourcedExhibit] = []
        for item in body.iterfind("items/item"):
            seq = _text(item, "seq")
            if seq is None or _text(item, "area") in self._excluded_areas:
                continue
            detail = self._get("/detail2", {"seq": seq}).find("items/item")
            items.append(_to_sourced(seq, item, detail))
        return SourcedExhibitPage(
            items=tuple(items), total_count=_to_int(body.findtext("totalCount"))
        )

    def _get(self, path: str, params: dict[str, str | int]) -> Element:
        try:
            response = self._http_client.get(
                f"{self._base_url}{path}",
                params={"serviceKey": self._service_key, **params},
            )
        except httpx.TransportError as error:
            _logger.warning(
                "open data request failed: path=%s error=%s",
                path,
                type(error).__name__,
            )
            raise ExhibitError.source_unavailable() from None
        if response.status_code != httpx.codes.OK:
            _logger.warning(
                "open data status: path=%s status=%d", path, response.status_code
            )
            raise ExhibitError.source_unavailable()
        try:
            root = fromstring(response.content)
        except ParseError, DefusedXmlException:
            _logger.warning("open data response unreadable: path=%s", path)
            raise ExhibitError.source_unavailable() from None
        result_code = root.findtext("header/resultCode")
        body = root.find("body")
        if result_code != SUCCESS_RESULT_CODE or body is None:
            _logger.warning("open data rejected: path=%s code=%s", path, result_code)
            raise ExhibitError.source_unavailable()
        return body


def _to_sourced(seq: str, item: Element, detail: Element | None) -> SourcedExhibit:
    area = _text(item, "area")
    return SourcedExhibit(
        external_id=seq,
        title=_text(item, "title"),
        description=_detail_text(detail, "contents1"),
        poster_url=_text(item, "thumbnail") or _detail_text(detail, "imgUrl"),
        ticket_url=_detail_text(detail, "url"),
        start_date=_to_iso_date(_text(item, "startDate")),
        end_date=_to_iso_date(_text(item, "endDate")),
        place_name=_text(item, "place"),
        country=DOMESTIC_COUNTRY_NAME,
        region=None if area is None else REGION_BY_AREA.get(area, area),
        address=_detail_text(detail, "placeAddr"),
        phone=_detail_text(detail, "phone"),
        latitude=_text(item, "gpsY"),
        longitude=_text(item, "gpsX"),
    )


def _text(element: Element, tag: str) -> str | None:
    value = element.findtext(tag)
    if value is None:
        return None
    text = unescape(value).strip()
    return text or None


def _detail_text(detail: Element | None, tag: str) -> str | None:
    return None if detail is None else _text(detail, tag)


def _to_iso_date(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return datetime.strptime(value, SOURCE_DATE_FORMAT).date().isoformat()
    except ValueError:
        return value


def _to_int(value: str | None) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0
