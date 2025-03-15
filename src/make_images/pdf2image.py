import logging
from pathlib import Path
from typing import List, Optional

import pymupdf as fitz
from PIL import Image

from ..config.settings import settings

logger = logging.getLogger(__name__)

DEFAULT_DPI = 72


def page2image(page: fitz.Page, downscale: float = 1.0) -> Image.Image:
    # Convert page to pixmap
    new_dpi = int(DEFAULT_DPI / downscale)
    pix = page.get_pixmap(dpi=new_dpi)  # pyright: ignore

    # Convert pixmap to PIL Image
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    # Resize image to original size
    img = img.resize((int(pix.width * downscale), int(pix.height * downscale)))
    return img


def pdf2images(
    path: Path, downscale: float = 1.0, idxs: Optional[List[int]] = None
) -> List[Image.Image]:
    doc = fitz.open(path)
    images = []
    for idx in idxs or range(doc.page_count):
        page = doc.load_page(idx)
        img = page2image(page, downscale=downscale)
        images.append(img)
    return images


def pdfs_folder_to_attack_images(
    downscale: float = 4.0, pdf_dir: Path = settings.data_path / "pdf"
) -> List[Image.Image]:
    pdfs = list(pdf_dir.glob("*.pdf"))
    all_images = []
    save_folder = settings.attack_images_path / "pdf"
    for path in pdfs:
        images = pdf2images(path, downscale=downscale)
        for idx, img in enumerate(images):
            img.save(save_folder / f"{path.stem}__{idx}.png")
            logger.info(f"Saved image {path.stem}__{idx}.png")
        all_images.extend(images)
    return all_images


def run_pdf2images(
    downscale: float = 4.0, pdf_dir: Path = settings.data_path / "pdf"
) -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--downscale", type=float, default=4.0)
    args = parser.parse_args()
    downscale = args.downscale
    images = pdfs_folder_to_attack_images(downscale=downscale)
    print(f"Total images: {len(images)}")


if __name__ == "__main__":
    run_pdf2images()
