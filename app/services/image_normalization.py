import io

import pillow_heif
from PIL import Image, UnidentifiedImageError

from app.core.errors import ExtractionError

pillow_heif.register_heif_opener()

_MAX_DIMENSION = 2048
_JPEG_QUALITY = 90


def normalize_image(image_bytes: bytes, filename: str) -> tuple[bytes, str]:
    """Re-encodes an uploaded image (any Pillow/HEIC-openable format) as a size-capped JPEG.

    Some vision APIs reject HEIC/HEIF (common for iPhone photos) or are strict about
    the declared MIME type matching the actual content, so every upload is normalized
    here rather than trusting the browser-supplied Content-Type. Downscaling + JPEG
    re-encoding also keeps full-resolution phone photos (small as compressed HEIC, but
    huge once decoded) under providers' request-size limits.
    """
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img = img.convert("RGB")
            if max(img.size) > _MAX_DIMENSION:
                img.thumbnail((_MAX_DIMENSION, _MAX_DIMENSION), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=_JPEG_QUALITY)
            return buf.getvalue(), "image/jpeg"
    except UnidentifiedImageError as e:
        raise ExtractionError(f"Could not read '{filename}' as an image. Please upload a JPEG, PNG, HEIC, or WEBP file.") from e
