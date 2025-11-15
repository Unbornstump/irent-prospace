# html_utils.py

def build_picture_tag(image_obj):
    """
    Generates <picture> tag using WebP, mobile JPG & desktop JPG.
    """
    return f"""
    <picture>
        <source srcset="{image_obj.webp.url}" type="image/webp">
        <source srcset="{image_obj.mobile.url}" media="(max-width: 768px)">
        <img src="{image_obj.desktop.url}" alt="Property image" loading="lazy">
    </picture>
    """
