import json
import logging
from pathlib import Path
from typing import List

from pydantic import BaseModel

from src.config.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=settings.logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
)


class PdfDescription(BaseModel):
    filename: str
    description: str

    @property
    def image_path(self) -> Path:
        pdf_dir_path = settings.attack_images_path / "pdf"
        path = None
        for fpath in pdf_dir_path.glob("*.png"):
            if self.filename in fpath.stem:
                path = fpath
                break
        if path is None:
            raise FileNotFoundError(f"Image not found: {path}")
        logger.info(f"Image found: {path}")
        return path


def load_pdf_descriptions() -> List[PdfDescription]:
    pdf_descriptions_path = settings.data_path / "pdf/pdf_descriptions.json"
    if not pdf_descriptions_path.exists():
        raise FileNotFoundError(
            f"PDF descriptions file not found: {pdf_descriptions_path}"
        )
    pdf_descriptions = json.loads(pdf_descriptions_path.read_text())
    logger.info(f"Loaded {len(pdf_descriptions)} PDF descriptions")
    print(f"Loaded {len(pdf_descriptions)} PDF descriptions")
    return [PdfDescription(**pdf) for pdf in pdf_descriptions]
