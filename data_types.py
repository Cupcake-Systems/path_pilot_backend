from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    user_id: str


class LogEntry(BaseModel):
    message: str
    time: datetime
    level: str
