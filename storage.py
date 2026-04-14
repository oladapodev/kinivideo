from __future__ import annotations

from pathlib import Path

from config import settings
from models import AssetRef, SourceType


class LocalStorage:
    def __init__(self) -> None:
        settings.asset_dir.mkdir(parents=True, exist_ok=True)
        settings.export_dir.mkdir(parents=True, exist_ok=True)

    def save_bytes(
        self,
        *,
        file_name: str,
        content_type: str,
        data: bytes,
        source_type: SourceType,
        origin_url: str | None = None,
    ) -> AssetRef:
        path = settings.asset_dir / file_name
        path.write_bytes(data)
        return AssetRef(
            storage_key=str(path),
            filename=file_name,
            content_type=content_type,
            source_type=source_type,
            origin_url=origin_url,
        )

    def export_path(self, clip_id: str, suffix: str) -> Path:
        return settings.export_dir / f"{clip_id}{suffix}"


storage = LocalStorage()
