from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import boto3
import firebase_admin
import httpx
from botocore.config import Config
from fastapi import FastAPI
from firebase_admin import credentials
from jwt import PyJWKClient
from redis import Redis

from arttrip.application.domain.auth.social_provider import SocialProvider
from arttrip.application.domain.exhibit.exhibit_status_policy import ExhibitStatusPolicy
from arttrip.application.domain.search_history.search_history_policy import (
    SearchHistoryPolicy,
)
from arttrip.application.domain.user.profile_image_policy import ProfileImagePolicy
from arttrip.common import settings
from arttrip.inbound.http.web_session import WebSessionPolicy
from arttrip.outbound.fcm.fcm_push_adapter import FcmPushAdapter
from arttrip.outbound.oauth.oidc_adapter import OidcOAuthAdapter
from arttrip.outbound.oauth.provider_config import PROVIDER_CONFIGS
from arttrip.outbound.oauth.web_oauth_adapter import (
    GOOGLE_AUTHORIZATION_ENDPOINT,
    GOOGLE_TOKEN_ENDPOINT,
    WebOAuthAdapter,
    WebProviderConfig,
)
from arttrip.outbound.opendata.culture_info_adapter import (
    CultureInfoExhibitSourceAdapter,
)
from arttrip.outbound.persistence.engine import (
    create_database_engine,
    create_session_factory,
)
from arttrip.outbound.persistence.models.all import map_tables
from arttrip.outbound.redis.access_token_denylist_adapter import (
    RedisAccessTokenDenylistAdapter,
)
from arttrip.outbound.redis.refresh_token_adapter import RedisRefreshTokenAdapter
from arttrip.outbound.redis.today_exhibit_cache_adapter import (
    RedisTodayExhibitCacheAdapter,
)
from arttrip.outbound.s3.image_storage_adapter import S3ImageStorageAdapter
from arttrip.outbound.token.jwt_adapter import JwtTokenAdapter


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    map_tables()

    engine = create_database_engine(settings.db)
    app.state.session_factory = create_session_factory(engine)
    app.state.oauth = OidcOAuthAdapter(
        jwk_clients={
            provider: PyJWKClient(
                config.jwks_uri, timeout=settings.oauth.timeout_seconds
            )
            for provider, config in PROVIDER_CONFIGS.items()
        },
        audiences={
            SocialProvider.APPLE: settings.oauth.apple_audiences,
            SocialProvider.GOOGLE: [settings.web_auth.google_client_id],
            SocialProvider.KAKAO: settings.oauth.kakao_audiences,
        },
        leeway_seconds=settings.oauth.leeway_seconds,
    )
    redis_client = Redis.from_url(settings.redis.url, decode_responses=True)
    app.state.refresh_tokens = RedisRefreshTokenAdapter(
        client=redis_client,
        expiration_seconds=settings.jwt.refresh_expiration,
    )
    app.state.access_token_denylist = RedisAccessTokenDenylistAdapter(
        client=redis_client
    )
    app.state.today_exhibit_cache = RedisTodayExhibitCacheAdapter(client=redis_client)

    app.state.token = JwtTokenAdapter(
        issuer=settings.jwt.issuer,
        secret=settings.jwt.secret.get_secret_value(),
        access_expiration_seconds=settings.jwt.access_expiration,
    )
    app.state.exhibit_status_policy = ExhibitStatusPolicy(
        ending_soon_days=settings.exhibit.ending_soon_days
    )
    oauth_http_client = httpx.Client(timeout=settings.oauth.timeout_seconds)
    app.state.web_oauth = WebOAuthAdapter(
        http_client=oauth_http_client,
        configs={
            SocialProvider.GOOGLE: WebProviderConfig(
                authorization_endpoint=GOOGLE_AUTHORIZATION_ENDPOINT,
                token_endpoint=GOOGLE_TOKEN_ENDPOINT,
                client_id=settings.web_auth.google_client_id,
                client_secret=settings.web_auth.google_client_secret.get_secret_value(),
                redirect_uri=settings.web_auth.google_redirect_uri,
                scope="openid email",
            ),
        },
    )
    app.state.web_session_policy = WebSessionPolicy(
        secure=settings.web_auth.cookie_secure,
        samesite=settings.web_auth.cookie_samesite,
        access_max_age_seconds=settings.jwt.access_expiration,
        refresh_max_age_seconds=settings.jwt.refresh_expiration,
        state_max_age_seconds=settings.web_auth.state_max_age_seconds,
        success_redirect_url=settings.web_auth.success_redirect_url,
        failure_redirect_url=settings.web_auth.failure_redirect_url,
        allowed_origins=frozenset(settings.web_auth.allowed_origins),
    )

    s3_client = boto3.session.Session().client(
        "s3",
        region_name=settings.s3.s3_region,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "virtual"},
            connect_timeout=settings.s3.s3_connect_timeout_seconds,
            read_timeout=settings.s3.s3_read_timeout_seconds,
            retries={"max_attempts": settings.s3.s3_max_attempts, "mode": "standard"},
        ),
    )
    app.state.image_storage = S3ImageStorageAdapter(
        client=s3_client,
        bucket=settings.s3.s3_bucket_name,
        # public_base_url="https://" + settings.s3.cloudfront_domain,
        url_expires_seconds=settings.s3.s3_url_expires_seconds,
        key_prefix=settings.s3.s3_key_prefix,
    )
    app.state.profile_image_policy = ProfileImagePolicy(
        default_key=settings.image.default_profile_key
    )

    app.state.search_history_policy = SearchHistoryPolicy(
        max_count=settings.search_history.max_count,
        max_length=settings.search_history.max_length,
    )

    firebase_app = firebase_admin.initialize_app(
        credentials.Certificate(settings.push.firebase_credentials_path),
        options={"httpTimeout": settings.push.timeout_seconds},
    )
    app.state.push_sender = FcmPushAdapter(app=firebase_app)

    opendata_http_client = httpx.Client(timeout=settings.opendata.timeout_seconds)
    app.state.exhibit_source = CultureInfoExhibitSourceAdapter(
        http_client=opendata_http_client,
        base_url=settings.opendata.base_url,
        service_key=settings.opendata.service_key.get_secret_value(),
        excluded_areas=frozenset(settings.opendata.excluded_areas),
    )

    yield

    engine.dispose()
    redis_client.close()
    oauth_http_client.close()
    s3_client.close()
    firebase_admin.delete_app(firebase_app)
    opendata_http_client.close()
