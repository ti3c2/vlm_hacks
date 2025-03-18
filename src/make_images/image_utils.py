import base64
import io
from pathlib import Path

from PIL import Image


def lower_image_resolution(img: Image.Image, rescale: float = 0.25):
    pass


def image2base64(pil_image: Image.Image):
    buffered = io.BytesIO()
    pil_image.save(buffered, format="png")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str.decode("utf-8")


def imgfile2base64(img_path: Path):
    img = Image.open(img_path)
    return image2base64(img)
