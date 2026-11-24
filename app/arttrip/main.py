import logging

from arttrip.bootstrap.lifespan import lifespan
from arttrip.bootstrap.wiring import wire
from arttrip.common import settings
from arttrip.inbound.http.app import create_app

logging.basicConfig(
    level=settings.log.level,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
)

app = create_app(
    lifespan=lifespan,
    docs_enabled=settings.http.docs_enabled,
    allowed_origins=settings.web_auth.allowed_origins,
    max_body_bytes=settings.http.max_body_bytes,
)
wire(app)
