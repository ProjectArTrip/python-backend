import httpx
import pytest
from arttrip.application.util.exception import DomainException
from arttrip.outbound.opendata.culture_info_adapter import (
    CultureInfoExhibitSourceAdapter,
)

SERVICE_KEY = "test-service-key"


def adapter_returning(body: bytes) -> CultureInfoExhibitSourceAdapter:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, content=body))
    return CultureInfoExhibitSourceAdapter(
        http_client=httpx.Client(transport=transport),
        base_url="https://opendata.test",
        service_key=SERVICE_KEY,
        excluded_areas=frozenset(),
    )


class TestCultureInfoExhibitSourceAdapter:
    def test_엔티티를_선언한_응답은_읽지_않는다(self) -> None:
        # given
        payload = (
            b'<?xml version="1.0"?>'
            b'<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]>'
            b"<response><header><resultCode>00</resultCode></header>"
            b"<body><totalCount>&x;</totalCount></body></response>"
        )

        # when
        with pytest.raises(DomainException) as exc_info:
            adapter_returning(payload).fetch_page(page_no=1, size=1)

        # then
        assert exc_info.value.code == "EXHIBIT_SOURCE_UNAVAILABLE"

    def test_결과_코드가_정상이_아니면_실패로_알리고_키를_싣지_않는다(self) -> None:
        # given
        payload = (
            "<response><header><resultCode>30</resultCode>"
            "<resultMsg>등록되지 않은 서비스키</resultMsg></header></response>"
        ).encode()

        # when
        with pytest.raises(DomainException) as exc_info:
            adapter_returning(payload).fetch_page(page_no=1, size=1)

        # then
        assert exc_info.value.code == "EXHIBIT_SOURCE_UNAVAILABLE"
        assert SERVICE_KEY not in str(exc_info.value)
