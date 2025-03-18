import logging
from pathlib import Path
from typing import List, Optional

import pymupdf as fitz
from PIL import Image

from ..config.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=settings.logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
)

DEFAULT_DPI = 72


def page2image(page: fitz.Page, rescale: float = 1.0) -> Image.Image:
    # Convert page to pixmap
    new_dpi = int(DEFAULT_DPI * rescale)
    pix = page.get_pixmap(dpi=new_dpi)  # pyright: ignore

    # Convert pixmap to PIL Image
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    # Resize image to original size
    img = img.resize((int(pix.width / rescale), int(pix.height / rescale)))
    return img


def pdf2images(
    path: Path, rescale: float = 1.0, idxs: Optional[List[int]] = None
) -> List[Image.Image]:
    doc = fitz.open(path)
    images = []
    for idx in idxs or range(doc.page_count):
        page = doc.load_page(idx)
        img = page2image(page, rescale=rescale)
        images.append(img)
    return images


def pdfs_folder_to_attack_images(
    rescale: float = 0.25, pdf_dir: Path = settings.data_path / "pdf"
) -> List[Image.Image]:
    pdfs = list(pdf_dir.glob("*.pdf"))
    all_images = []
    save_folder = settings.attack_images_path / "pdf"
    save_folder.mkdir(parents=True, exist_ok=True)
    for path in pdfs:
        images = pdf2images(path, rescale=rescale)
        for idx, img in enumerate(images):
            fname = save_folder / f"{path.stem}__page_{idx+1}__rescale_{rescale}.png"
            img.save(fname)
            logger.info(f"Saved image {fname}")
        all_images.extend(images)
    return all_images


def run_pdf2images(
    rescale: float = 0.25, pdf_dir: Path = settings.data_path / "pdf"
) -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--rescale", type=float, default=0.25)
    args = parser.parse_args()
    rescale = args.rescale
    images = pdfs_folder_to_attack_images(rescale=rescale)
    print(f"Total images: {len(images)}")


if __name__ == "__main__":
    run_pdf2images()
