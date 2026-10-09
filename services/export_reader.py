"""Cancellable private local MinIO reads; no public URLs, redirects or provider logging."""

from datetime import UTC, datetime
from typing import cast
from urllib.parse import urlsplit
from uuid import UUID

import anyio
import httpx
from minio.credentials.credentials import Credentials
from minio.helpers import check_bucket_name
from minio.signer import sign_v4_s3

from services.config import Settings, require_local
from services.export_artifacts import MAX_CIPHERTEXT_BYTES, ArtifactError
from services.export_storage import object_key, storage_scope

READ_SECONDS = 5.0
EMPTY_DIGEST = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class PrivateExportReader:
    def __init__(
        self, settings: Settings, *, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        try:
            endpoint = urlsplit(require_local(settings.object_storage_endpoint, {"minio"}))
            if (
                endpoint.scheme not in {"http", "https"}
                or endpoint.path not in {"", "/"}
                or endpoint.query
                or endpoint.fragment
                or endpoint.username is not None
            ):
                raise ValueError("Invalid local endpoint")
            check_bucket_name(settings.object_storage_container, strict=True)
            self.base_url = endpoint._replace(path="", query="", fragment="").geturl()
            self.container = settings.object_storage_container
            self.scope = storage_scope(settings)
            self.credentials = Credentials(
                settings.object_storage_access_key.get_secret_value(),
                settings.object_storage_secret_key.get_secret_value(),
            )
            self.transport = transport or httpx.AsyncHTTPTransport(
                retries=0,
                trust_env=False,
                limits=httpx.Limits(max_connections=1, max_keepalive_connections=1),
            )
        except Exception:
            raise ArtifactError("EXPORT_READER_UNAVAILABLE") from None

    async def aclose(self) -> None:
        try:
            with anyio.fail_after(1, shield=True):
                await self.transport.aclose()
        except Exception:
            raise ArtifactError("EXPORT_OBJECT_READ_FAILED") from None

    async def get(self, generation: UUID, object_id: UUID) -> bytes:
        response = None
        try:
            key = object_key(generation, object_id, scope=self.scope)
            url = urlsplit(f"{self.base_url}/{self.container}/{key}")
            now = datetime.now(UTC)
            headers = sign_v4_s3(
                method="GET",
                url=url,
                region="us-east-1",  # Approved local MinIO's default region; no discovery call.
                headers={
                    "Host": url.netloc,
                    "X-Amz-Date": now.strftime("%Y%m%dT%H%M%SZ"),
                    "X-Amz-Content-Sha256": EMPTY_DIGEST,
                },
                credentials=self.credentials,
                content_sha256=EMPTY_DIGEST,
                date=now,
            )
            request = httpx.Request(
                "GET",
                url.geturl(),
                headers=cast(dict[str, str], headers),
                extensions={"timeout": {"connect": 2, "read": 5, "write": 2, "pool": 2}},
            )
            # Use the transport directly: AsyncClient logs private object paths at INFO.
            # The raw transport neither follows redirects nor reads environment proxy settings.
            with anyio.fail_after(READ_SECONDS):
                response = await self.transport.handle_async_request(request)
                if (
                    response.status_code != 200
                    or response.headers.get("Content-Encoding", "identity") != "identity"
                    or "Transfer-Encoding" in response.headers
                ):
                    raise ValueError("Invalid private object response")
                header = response.headers.get("Content-Length", "")
                if not header.isascii() or not header.isdecimal() or len(header) > 6:
                    raise ValueError("Invalid object length")
                size = int(header)
                if not 0 < size <= MAX_CIPHERTEXT_BYTES:
                    raise ValueError("Invalid object size")
                body = bytearray()
                async for part in response.aiter_raw(chunk_size=16384):
                    if len(body) + len(part) > size:
                        raise ValueError("Oversized object")
                    body.extend(part)
                if len(body) != size:
                    raise ValueError("Incomplete object")
                return bytes(body)
        except Exception:
            raise ArtifactError("EXPORT_OBJECT_READ_FAILED") from None
        finally:
            if response is not None:
                try:
                    with anyio.fail_after(1, shield=True):
                        await response.aclose()
                except Exception:
                    raise ArtifactError("EXPORT_OBJECT_READ_FAILED") from None
