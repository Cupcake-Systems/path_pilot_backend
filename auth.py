import base64
import hashlib
import hmac

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from data_types import User
from secret_key import VALIDATION_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = User(user_id=token)
    return user


def is_valid_secure_key(key, length=16):
    if len(key) < length:
        return False

    random_part = key[:-8]
    provided_signature = key[-8:]

    # Recompute HMAC signature
    expected_signature = base64.urlsafe_b64encode(
        hmac.new(VALIDATION_KEY.encode("utf-8"), random_part.encode(), hashlib.sha256).digest()
    ).decode('utf-8')[:8]

    return hmac.compare_digest(provided_signature, expected_signature)
