from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from fastapi import UploadFile

from models import AssetRef, SourceType
from storage import storage


class TikTokReplayAdapter:
    def ingest(self, source_ref: str) -> AssetRef:
        parsed = urlparse(source_ref)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Replay URL must start with http or https.")
        if "tiktok.com" not in parsed.netloc:
            raise ValueError("Currently only TikTok replay URLs are supported.")

        fake_payload = (
            b"Placeholder video asset for local development. Replace this with yt-dlp "
            b"fetch logic in the production source adapter."
        )
        filename = f"{Path(parsed.path).name or 'tiktok-replay'}.mp4"
        return storage.save_bytes(
            file_name=filename,
            content_type="video/mp4",
            data=fake_payload,
            source_type=SourceType.tiktok_replay,
            origin_url=source_ref,
        )


class LocalUploadAdapter:
    async def ingest(self, upload: UploadFile) -> AssetRef:
        data = await upload.read()
        if not data:
            raise ValueError("Uploaded file is empty.")

        filename = upload.filename or "upload.mp4"
        return storage.save_bytes(
            file_name=filename,
            content_type=upload.content_type or "video/mp4",
            data=data,
            source_type=SourceType.local_upload,
        )
