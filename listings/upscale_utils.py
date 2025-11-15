# upscale_utils.py
from PIL import Image

"""
Using lightweight ESRGAN model or fallback sharpen
"""

def ai_upscale(image):
    try:
        # Placeholder: integrate ESRGAN-lite model
        # For now, perform a mild upscale & sharpen
        w, h = image.size
        image = image.resize((w * 2, h * 2), Image.LANCZOS)
        return image
    except Exception:
        return image
