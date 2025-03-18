import logging
from pathlib import Path
from typing import List

from pydantic import BaseModel

from ..config.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=settings.logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TextImageDescription(BaseModel):
    source: str
    filename: str
    text: str

    @property
    def image_path(self) -> Path:
        text_dir_path = settings.attack_images_path / "txt" / self.source
        path = text_dir_path / f"{self.text.replace(' ', '_')[:30]}.png"
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        logger.info(f"Image found: {path}")
        return path


def load_text_descriptions(words_file: Path) -> List[TextImageDescription]:
    """Loads text descriptions from words file."""
    if not words_file.exists():
        raise FileNotFoundError(f"Words file not found: {words_file}")

    words = words_file.read_text().splitlines()
    descriptions = [
        TextImageDescription(
            source=words_file.stem, filename=word.replace(" ", "_")[:30], text=word
        )
        for word in words
    ]

    logger.info(f"Loaded {len(descriptions)} text descriptions")
    return descriptions
