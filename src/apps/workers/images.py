import logging
import uuid
from io import BytesIO

import boto3
import requests
from django.conf import settings
from PIL import Image

logger = logging.getLogger(__name__)

WIDTH = 320
HEIGHT = 230


def _storage_is_configured():
    return all(
        (
            settings.DO_SPACE_KEY,
            settings.DO_SPACE_SECRET,
            settings.DO_SPACE_REGION,
            settings.DO_SPACE_NAME,
        )
    )


def load_image(item, folder_name):
    image_url = item.get("image")
    if not image_url or not _storage_is_configured():
        return item

    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        height = int(float(image.size[1]) * float(WIDTH) / float(image.size[0]))
        if height >= HEIGHT:
            image = image.resize((WIDTH, height), Image.Resampling.LANCZOS)
            delta = height - HEIGHT
            image = image.crop((0, delta / 2, WIDTH, height - delta / 2))
        else:
            width = int(float(image.size[0]) * float(HEIGHT) / float(image.size[1]))
            image = image.resize((width, HEIGHT), Image.Resampling.LANCZOS)
            delta = width - WIDTH
            image = image.crop((delta / 2, 0, width - delta / 2, HEIGHT))
        if image.mode != "RGB":
            image = image.convert("RGB")

        output = BytesIO()
        image.save(output, "webp", quality=75)
        output.seek(0)
        filename = uuid.uuid4()
        client = boto3.session.Session().client(
            "s3",
            region_name=settings.DO_SPACE_REGION,
            endpoint_url=f"https://{settings.DO_SPACE_REGION}.digitaloceanspaces.com",
            aws_access_key_id=settings.DO_SPACE_KEY,
            aws_secret_access_key=settings.DO_SPACE_SECRET,
        )
        key = f"{folder_name}/{filename}.webp"
        client.upload_fileobj(
            output,
            settings.DO_SPACE_NAME,
            key,
            ExtraArgs={"ContentType": "image/webp", "ACL": "public-read"},
        )
        item["image"] = (
            f"https://{settings.DO_SPACE_NAME}.{settings.DO_SPACE_REGION}.digitaloceanspaces.com/{key}"
        )
    except Exception:
        logger.exception("Could not mirror image %s", image_url)
    return item
