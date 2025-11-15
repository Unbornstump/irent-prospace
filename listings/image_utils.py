from PIL import Image, ImageEnhance
from io import BytesIO
from django.core.files import File
import os
import warnings

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
    use_face_preserve_crop=True
):
    """
    Full image optimization pipeline:
    - oversize file warning
    - desktop JPG
    - mobile JPG
    - WebP
    - optional face-preserving crop
    - sharpness improvement
    """

    warning = None

    # --- 1. Oversized file warning ---
    size_mb = image_file.size / (1024 * 1024)
    if size_mb > max_file_size_mb:
        warning = (
            f"Image is {size_mb:.2f}MB — exceeds recommended {max_file_size_mb}MB. "
            "It has been compressed."
        )

    # --- 2. Load image ---
    img = Image.open(image_file)

    if img.mode in ("RGBA", "P"):
        rgb = Image.new("RGB", img.size, (255, 255, 255))
        rgb.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = rgb

    # --- 3. Face-aware cropping ---
    if use_face_preserve_crop and FACE_LIB_AVAILABLE:
        try:
            import face_recognition
            raw_img = face_recognition.load_image_file(image_file)
            faces = face_recognition.face_locations(raw_img)

            if faces:
                top, right, bottom, left = faces[0]
                padding = 200
                left = max(left - padding, 0)
                top = max(top - padding, 0)
                right = min(right + padding, img.width)
                bottom = min(bottom + padding, img.height)
                img = img.crop((left, top, right, bottom))

        except Exception:
            warnings.warn("Face detection failed; continuing without crop.")

    # --- 4. Sharpness enhancement ---
    if enhance_sharpness:
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.25)

    base_name, _ = os.path.splitext(image_file.name)

    # --- 5. Desktop version ---
    desktop_img = img.copy()
    desktop_img.thumbnail((max_width, max_height), Image.LANCZOS)

    desktop_io = BytesIO()
    desktop_img.save(desktop_io, "JPEG", quality=jpeg_quality)
    desktop_io.seek(0)

    desktop_file = File(desktop_io, name=f"{base_name}_desktop.jpg")

    # --- 6. Mobile version ---
    mobile_img = img.copy()
    mobile_img.thumbnail((mobile_width, mobile_height), Image.LANCZOS)

    mobile_io = BytesIO()
    mobile_img.save(mobile_io, "JPEG", quality=mobile_quality)
    mobile_io.seek(0)

    mobile_file = File(mobile_io, name=f"{base_name}_mobile.jpg")

    # --- 7. WebP version ---
    webp_io = BytesIO()
    img.save(webp_io, "WEBP", quality=webp_quality)
    webp_io.seek(0)

    webp_file = File(webp_io, name=f"{base_name}.webp")

    return {
        "desktop": desktop_file,
        "mobile": mobile_file,
        "webp": webp_file,
        "warning": warning
    }
