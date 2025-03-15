import base64

from PIL import Image


def lower_image_resolution():
    pass


def image_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
