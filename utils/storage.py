"""Bunny.net object storage backend for Django FileField / ImageField."""

from __future__ import annotations

import mimetypes
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class BunnyStorage(Storage):
    def __init__(
        self,
        zone=None,
        api_key=None,
        hostname=None,
        cdn_url=None,
        timeout=None,
    ):
        self.zone = zone or settings.BUNNY_STORAGE_ZONE
        self.api_key = api_key or settings.BUNNY_STORAGE_API_KEY
        self.hostname = (hostname or settings.BUNNY_STORAGE_HOSTNAME).rstrip("/")
        self.cdn_url = (cdn_url or settings.BUNNY_CDN_URL).rstrip("/")
        self.timeout = timeout or getattr(settings, "BUNNY_STORAGE_TIMEOUT", 60)

    def _encoded_path(self, name: str) -> str:
        clean = name.lstrip("/")
        return "/".join(quote(segment, safe="") for segment in clean.split("/"))

    def _object_url(self, name: str) -> str:
        return f"https://{self.hostname}/{self.zone}/{self._encoded_path(name)}"

    def _request(self, method: str, name: str, data: bytes | None = None, headers=None):
        req_headers = {"AccessKey": self.api_key}
        if headers:
            req_headers.update(headers)
        request = Request(
            self._object_url(name),
            data=data,
            headers=req_headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = response.read()
                return response.status, body, dict(response.headers)
        except HTTPError as exc:
            body = exc.read() if exc.fp else b""
            return exc.code, body, dict(exc.headers or {})
        except URLError as exc:
            raise OSError(f"Bunny storage request failed: {exc}") from exc

    def _open(self, name, mode="rb"):
        if "w" in mode or "a" in mode or "+" in mode:
            raise ValueError("BunnyStorage open only supports read modes.")
        status, body, _ = self._request("GET", name)
        if status != 200:
            raise FileNotFoundError(f"Bunny object not found: {name}")
        return ContentFile(body, name=name)

    def put_bytes(self, name: str, payload: bytes, content_type: str | None = None) -> str:
        """Upload exactly to `name` (no get_available_name rename)."""
        clean = name.lstrip("/")
        ctype = content_type or mimetypes.guess_type(clean)[0] or "application/octet-stream"
        status, body, _ = self._request(
            "PUT",
            clean,
            data=payload,
            headers={"Content-Type": ctype},
        )
        if status not in (200, 201):
            detail = body.decode("utf-8", errors="replace")[:300]
            raise OSError(f"Bunny upload failed ({status}) for {clean}: {detail}")
        return clean

    def _save(self, name, content):
        name = self.get_available_name(name)
        if hasattr(content, "chunks"):
            payload = b"".join(chunk for chunk in content.chunks())
        else:
            payload = content.read()
        return self.put_bytes(name, payload)

    def delete(self, name):
        if not name:
            return
        status, _, _ = self._request("DELETE", name)
        if status not in (200, 204, 404):
            raise OSError(f"Bunny delete failed ({status}) for {name}")

    def exists(self, name):
        status, _, _ = self._request("HEAD", name)
        if status in (200, 404):
            return status == 200
        status, _, _ = self._request("GET", name)
        return status == 200

    def size(self, name):
        status, body, headers = self._request("HEAD", name)
        if status == 200:
            length = headers.get("Content-Length")
            if length is not None:
                return int(length)
        status, body, headers = self._request("GET", name)
        if status != 200:
            raise FileNotFoundError(f"Bunny object not found: {name}")
        length = headers.get("Content-Length")
        if length is not None:
            return int(length)
        return len(body)

    def url(self, name):
        return f"{self.cdn_url}/{self._encoded_path(name or '')}"

    def get_accessed_time(self, name):
        raise NotImplementedError("BunnyStorage does not support accessed time.")

    def get_created_time(self, name):
        raise NotImplementedError("BunnyStorage does not support created time.")

    def get_modified_time(self, name):
        raise NotImplementedError("BunnyStorage does not support modified time.")
