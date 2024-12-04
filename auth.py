from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from data_types import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = User(user_id=token)
    return user
