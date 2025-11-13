from PIL import Image
from io import BytesIO
from django.core.files import File
import os

def resize_image(image_file, max_width=1024, max_height=1024, quality=85):
    """
    Resize and compress an uploaded image.
    Returns a new InMemoryUploadedFile (ready to save).
    """
    img = Image.open(image_file)

    # Convert RGBA to RGB if needed
    if img.mode in ("RGBA", "P"):
        rgb = Image.new("RGB", img.size, (255, 255, 255))
        rgb.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = rgb

    img.thumbnail((max_width, max_height), Image.LANCZOS)

    thumb_io = BytesIO()
    img.save(thumb_io, format='JPEG', quality=quality)
    thumb_io.seek(0)

    # Build a simple name
    name, _ = os.path.splitext(image_file.name)
    new_name = f"{name}_resized.jpg"

    return File(thumb_io, name=new_name)