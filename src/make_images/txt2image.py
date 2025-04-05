import logging
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from src.config.settings import PROJECT_PATH, settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=settings.logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
)


def txt2image(
    text: str,
    img_size: Tuple[int, int] = (600, 400),
    max_words_per_line: int = 3,
) -> Image.Image:
    """Creates an image with text, wrapping lines by max_words_per_line words."""
    img = Image.new("RGB", img_size, color="white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=50)

    # Split text into lines
    words = text.split()
    lines = [
        " ".join(words[i : i + max_words_per_line])
        for i in range(0, len(words), max_words_per_line)
    ]
    text_width = max([draw.textbbox((0, 0), line, font=font)[2] for line in lines])

    # Calculate text height
    text_height = draw.textbbox((0, 0), "Ay", font=font)[3]
    total_height = img_size[1]

    # Create image with required size
    img = Image.new("RGB", (img_size[0], total_height + 20), color="white")
    draw = ImageDraw.Draw(img)

    # Draw text
    y_offset = total_height // 3
    for line in lines:
        x_position = (img_size[0] - text_width) // 2
        draw.text((x_position, y_offset), line, font=font, fill="black")
        y_offset += text_height

    return img


def create_text_images(
    words_file: Path,
    txt_dir: Path = settings.attack_images_path / "txt",
    crop: Optional[int] = None,
) -> None:
    """Creates images for all words in the input file."""
    save_dir = txt_dir / words_file.stem
    save_dir.mkdir(parents=True, exist_ok=True)

    words = words_file.read_text().splitlines()
    for word in words:
        img = txt2image(word)
        fname_str = word.replace(" ", "_")
        if crop is not None:
            fname_str = fname_str[:crop]
        fname = save_dir / f"{fname_str}.png"
        img.save(fname)
        logger.info(f"Saved image {fname.relative_to(PROJECT_PATH)}")
    logger.info(f"Total images for {words_file.stem}: {len(words)}")


def run_text2images() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--words_file", type=Path, default=None)
    args = parser.parse_args()

    if args.words_file is not None:
        create_text_images(args.words_file)
    else:
        txt_dir = settings.data_path / "txt"
        for fpath in txt_dir.glob("*.txt"):
            create_text_images(fpath)


if __name__ == "__main__":
    run_text2images()
