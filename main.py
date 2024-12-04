from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from fastapi.params import Header
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from auth import get_current_user, is_valid_secure_key
from data_types import User, LogEntry

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./logs.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database model
class LogEntryModel(Base):
    __tablename__ = "log_entries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    time = Column(DateTime, nullable=False)
    message = Column(String, nullable=False)
    level = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/logs/submit")
async def submit_log(
        log_submissions: list[LogEntry], validation_token: Annotated[str, Header()],
        current_user: User = Depends(get_current_user), db=Depends(get_db),
):
    if not is_valid_secure_key(validation_token):
        raise HTTPException(status_code=403, detail="Invalid validation token.")

    log_entries = [
        LogEntryModel(
            user_id=current_user.user_id,
            message=log.message,
            level=log.level,
            time=log.time,
        )
        for log in log_submissions
    ]
    db.add_all(log_entries)
    db.commit()

    return {"message": f"Successfully submitted {len(log_entries)} logs."}
