from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.params import Header
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from starlette.staticfiles import StaticFiles

from auth import get_current_user, is_valid_secure_key
from data_types import User, LogEntry
from secret_key import DEV_PASSWORDS

app = FastAPI(docs_url=None, redoc_url=None)

# Database setup
DATABASE_URL = "sqlite:///./logs.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# User model
class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    logs = relationship("LogEntryModel", back_populates="user")


# Log entry model
class LogEntryModel(Base):
    __tablename__ = "log_entries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    time = Column(DateTime, nullable=False, index=True)
    message = Column(String, nullable=False)
    level = Column(String, nullable=False)

    user = relationship("UserModel", back_populates="logs")

    # Index for faster queries by user and time
    __table_args__ = (Index("ix_user_time", "user_id", "time"),)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/logs")
async def get_logs(
        user_id: Annotated[str, Header()],
        dev_username: Annotated[str, Header()],
        dev_password: Annotated[str, Header()],
        db=Depends(get_db),
):
    if DEV_PASSWORDS.get(dev_username) != dev_password:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Ensure the user exists in the database
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch logs
    logs = db.query(LogEntryModel).filter(LogEntryModel.user_id == user.id).all()
    return logs


@app.post("/logs/submit")
async def submit_log(
        log_submissions: list[LogEntry],
        validation_token: Annotated[str, Header()],
        current_user: User = Depends(get_current_user),
        db=Depends(get_db),
):
    if not is_valid_secure_key(validation_token):
        raise HTTPException(status_code=403, detail="Invalid validation token.")

    # Ensure the user exists in the database
    user = db.query(UserModel).filter(UserModel.user_id == current_user.user_id).first()
    if not user:
        user = UserModel(user_id=current_user.user_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Insert log entries
    log_entries = [
        LogEntryModel(
            user_id=user.id,
            time=log.time,
            message=log.message,
            level=log.level,
        )
        for log in log_submissions
    ]
    db.add_all(log_entries)
    db.commit()

    return {"message": f"Successfully submitted {len(log_entries)} logs."}


app.mount("/", StaticFiles(directory="static"), name="static")
