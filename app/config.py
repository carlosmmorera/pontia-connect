import os

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
    GOOGLE_SEARCH_API_KEY: str
    GOOGLE_SEARCH_ENGINE_ID: str

    # Agent Constants
    AGENT_MODEL: str = "gemini-2.5-pro"
    ATTENDEE_RANGE: str = "Attendees!A2:C"
    MATCH_THRESHOLD: int = 75

    AGENT_SYSTEM_PROMPT: str = (
        "You are an elite networking assistant for the 'Pontia Connect' AI Master's event. "
        "When asked to help network with someone, follow this Action Plan:\n"
        "1. REASONING: Explain your thought process out loud.\n"
        "2. ACTION: Look up their data in the attendee database.\n"
        "3. ACTION: Search the internet for recent news about their company.\n"
        "4. SYNTHESIS: Write a short, highly personalized 2-sentence icebreaker "
        "combining their role and the recent company news.\n\n"
        "Format your final response clearly, showing the 'REASONING' block before the 'ICEBREAKER'."
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    settings = Settings() # type: ignore

    os.environ["GOOGLE_CLOUD_PROJECT"] = settings.GOOGLE_CLOUD_PROJECT
    os.environ["GOOGLE_CLOUD_LOCATION"] = settings.GOOGLE_CLOUD_LOCATION
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = str(settings.GOOGLE_GENAI_USE_VERTEXAI)

    return settings