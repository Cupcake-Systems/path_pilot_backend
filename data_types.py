from pydantic import BaseModel


class User(BaseModel):
    user_id: str


class LogEntry(BaseModel):
    message: str
    time: str
    level: str