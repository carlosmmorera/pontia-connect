import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import Field


class Settings(BaseSettings):
    APP_NAME: str = "pontia-connect-app"

    # GCP Infrastructure Settings
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str
    GOOGLE_GENAI_USE_VERTEXAI: bool = True

    # External Integrations
    SPREADSHEET_ID: str = Field(alias="PONTIA_CONNECT_SHEET_ID")

    # Agent Constants
    AGENT_MODEL: str = "gemini-2.5-pro"
    ATTENDEE_RANGE: str = "Attendees!A2:C"
    MATCH_THRESHOLD: int = 75

    PROMPTS_DIR: Path = Path(__file__).parent / "ai" / "prompts"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    settings = Settings() # type: ignore

    os.environ["GOOGLE_CLOUD_PROJECT"] = settings.GOOGLE_CLOUD_PROJECT
    os.environ["GOOGLE_CLOUD_LOCATION"] = settings.GOOGLE_CLOUD_LOCATION
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = str(settings.GOOGLE_GENAI_USE_VERTEXAI)

    return settings