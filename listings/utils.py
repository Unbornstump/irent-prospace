# image_utils.py
from PIL import Image, ImageEnhance
from io import BytesIO
from django.core.files import File
import os
import warnings

# Local imports
from .security_utils import scan_image_for_malware
from .cache_utils import get_image_hash, check_hash_exists, store_hash
from .upscale_utils import ai_upscale


try:
    import face_recognition
    FACE_LIB_AVAILABLE = True
except ImportError:
    FACE_LIB_AVAILABLE = False


def resize_and_optimize_image(
    image_file,
    max_width=1200,
    max_height=1200,
    mobile_width=720,
    mobile_height=720,
    jpeg_quality=85,
    mobile_quality=65,
    webp_quality=70,
    max_file_size_mb=8,
    enhance_sharpness=True,
    use_face_preserve_crop=True,
    use_ai_upscale=True
):
    """
    FULL FEATURED image pipeline:
    --------------------------------
    ✔ Virus scanning
    ✔ Detect duplicates (hash)
    ✔ Optional AI-upscale for blurry images
    ✔ Face-aware smart cropping
    ✔ Desktop JPG + mobile JPG + WebP output
    ✔ Sharpness enhancement
    ✔ Oversize file warnings
    ✔ Returns: {desktop, mobile, webp, duplicate, warning}
    """

    # ===========================
    # 1. MALWARE SCANNING
    # ===========================
    scan_result = scan_image_for_malware(image_file)
    if scan_result is not True:
        return {"error": scan_result}  # Return malware reason

    # ===========================
    # 2. HASH & DEDUPLICATION
    # ===========================
    img_hash = get_image_hash(image_file)

    if check_hash_exists(img_hash):
        return {"duplicate": True, "hash": img_hash}

    # ===========================
    # 3. FILE SIZE CHECK
    # ===========================
    size_mb = image_file.size / (1024 * 1024)
    warning = None

    if size_mb > max_file_size_mb:
        warning = f"Image is {size_mb:.2f}MB — will be compressed."

    # ===========================
    # 4. LOAD IMAGE
    # ===========================
    img = Image.open(image_file)

    # Convert transparent PNG/WebP → white JPEG
    if img.mode in ("RGBA", "P"):
        rgb = Image.new("RGB", img.size, (255, 255, 255))
        rgb.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = rgb

    # ===========================
    # 5. OPTIONAL AI UPSCALING
    # ===========================
    if use_ai_upscale:
        img = ai_upscale(img)

    # ===========================
    # 6. FACE-AWARE CROPPING
    # ===========================
    if use_face_preserve_crop and FACE_LIB_AVAILABLE:
        try:
            raw = face_recognition.load_image_file(image_file)
            faces = face_recognition.face_locations(raw)

            if faces:
                top, right, bottom, left = faces[0]
                pad = 200
                left = max(left - pad, 0)
                top = max(top - pad, 0)
                right = min(right + pad, img.width)
                bottom = min(bottom + pad, img.height)
                img = img.crop((left, top, right, bottom))

        except Exception:
            warnings.warn("Face crop failed. Using original image.")

    # ===========================
    # 7. SHARPNESS ENHANCEMENT
    # ===========================
    if enhance_sharpness:
        img = ImageEnhance.Sharpness(img).enhance(1.25)

    # ===========================
    # 8. DESKTOP VERSION
    # ===========================
    desktop = img.copy()
    desktop.thumbnail((max_width, max_height), Image.LANCZOS)
    desk_io = BytesIO()
    desktop.save(desk_io, "JPEG", quality=jpeg_quality)
    desk_io.seek(0)
    base, _ = os.path.splitext(image_file.name)
    desktop_file = File(desk_io, name=f"{base}_desktop.jpg")

    # ===========================
    # 9. MOBILE VERSION
    # ===========================
    mobile = img.copy()
    mobile.thumbnail((mobile_width, mobile_height), Image.LANCZOS)
    mob_io = BytesIO()
    mobile.save(mob_io, "JPEG", quality=mobile_quality)
    mob_io.seek(0)
    mobile_file = File(mob_io, name=f"{base}_mobile.jpg")

    # ===========================
    # 10. WEBP VERSION
    # ===========================
    web_io = BytesIO()
    img.save(web_io, "WEBP", quality=webp_quality)
    web_io.seek(0)
    webp_file = File(web_io, name=f"{base}.webp")

    # Mark this hash as used
    store_hash(img_hash)

    return {
        "desktop": desktop_file,
        "mobile": mobile_file,
        "webp": webp_file,
        "warning": warning,
        "duplicate": False,
        "hash": img_hash,
    }
