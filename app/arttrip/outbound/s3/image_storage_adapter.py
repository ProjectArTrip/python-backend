from botocore.exceptions import BotoCoreError, ClientError
from mypy_boto3_s3 import S3Client

from arttrip.application.domain.image.exceptions import ImageError
from arttrip.application.port.output.image_storage_port import ImageStoragePort


class S3ImageStorageAdapter(ImageStoragePort):
    def __init__(
        self,
        *,
        client: S3Client,
        bucket: str,
        url_expires_seconds: int,
        key_prefix: str = "",
    ) -> None:
        self._client = client
        self._bucket = bucket
        self._url_expires_seconds = url_expires_seconds
        self._key_prefix = key_prefix.strip("/")

    def upload(self, *, key: str, content: bytes, content_type: str) -> None:
        try:
            self._client.put_object(
                Bucket=self._bucket,
                Key=self._object_key(key),
                Body=content,
                ContentType=content_type,
            )
        except (BotoCoreError, ClientError) as error:
            raise ImageError.storage_unavailable() from error

    def delete(self, key: str) -> None:
        try:
            self._client.delete_object(Bucket=self._bucket, Key=self._object_key(key))
        except (BotoCoreError, ClientError) as error:
            raise ImageError.storage_unavailable() from error

    def public_url(self, key: str) -> str:
        try:
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": self._object_key(key)},
                ExpiresIn=self._url_expires_seconds,
            )
        except (BotoCoreError, ClientError) as error:
            raise ImageError.storage_unavailable() from error

    def _object_key(self, key: str) -> str:
        return f"{self._key_prefix}/{key}" if self._key_prefix else key
