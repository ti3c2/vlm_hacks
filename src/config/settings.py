import logging
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_PATH = Path(__file__).parents[2]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # LLM settings
    openai_api_key: Optional[str] = Field(None)
    judge_model_name: str = "gpt-4o"
    judge_temperature: float = Field(default=0.1)
    openai_custom_endpoint: str = Field(default="http://localhost:1143/v1")

    # Data settings
    data_path: Path = PROJECT_PATH / "data"
    attack_images_path: Path = PROJECT_PATH / "data" / "attack_images"

    # Logging level
    logging_level: int = logging.INFO


# Create global settings instance
settings = Settings()  # pyright: ignore - using default arguments
