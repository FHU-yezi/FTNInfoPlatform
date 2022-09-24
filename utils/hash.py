from hashlib import sha512


def get_hash(text: str) -> str:
    return sha512(text.encode("utf-8")).hexdigest()[:15]
