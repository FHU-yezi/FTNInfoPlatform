from hashlib import sha512

import bcrypt


def get_hash(text: str) -> str:
    return sha512(text.encode("utf-8")).hexdigest()[:15]


def encrypt_password(password: str) -> str:
    hashed_password: bytes = get_hash(password).encode("utf-8")
    salt: bytes = bcrypt.gensalt()
    encrypted_password: bytes = bcrypt.hashpw(hashed_password, salt)
    return encrypted_password.decode("utf-8")


def check_password(user_input_password: str, encrypted_password: str) -> bool:
    user_input_password_bytes: bytes = get_hash(user_input_password).encode("utf-8")
    encrypted_password_bytes: bytes = encrypted_password.encode("utf-8")
    return bcrypt.checkpw(user_input_password_bytes, encrypted_password_bytes)
