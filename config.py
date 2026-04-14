from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "KiniVideo API"
    docs_url: str = "/docs"
    asset_dir: Path = Path("var/assets")
    export_dir: Path = Path("var/exports")


settings = Settings()
