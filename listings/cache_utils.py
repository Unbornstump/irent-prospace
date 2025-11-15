# cache_utils.py
import hashlib
from django.core.cache import cache

HASH_TIMEOUT = 60 * 60 * 24 * 7  # 7 days

def get_image_hash(file):
    hasher = hashlib.sha256()
    for chunk in file.chunks():
        hasher.update(chunk)
    file.seek(0)
    return hasher.hexdigest()

def check_hash_exists(image_hash):
    return cache.get(f"img_hash_{image_hash}") is not None

def store_hash(image_hash):
    cache.set(f"img_hash_{image_hash}", True, HASH_TIMEOUT)
