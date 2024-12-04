from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from auth import get_current_user
from data_types import User, LogEntry

# FastAPI app instance
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
    time = Column(DateTime, default=datetime.now)
    message = Column(String, nullable=False)
    level = Column(String, nullable=False)


# Create database schema
Base.metadata.create_all(bind=engine)


# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/logs/submit")
async def submit_log(
        log_submissions: list[LogEntry], current_user: User = Depends(get_current_user), db=Depends(get_db)
):
    # Save logs to the database
    log_entries = [
        LogEntryModel(
            user_id=current_user.user_id,
            message=log.message,
            level=log.level,
            time=log.time or datetime.now(),  # Default to now if no time is provided
        )
        for log in log_submissions
    ]
    db.add_all(log_entries)
    db.commit()
    return {"message": f"Successfully submitted {len(log_entries)} logs."}


@app.get("/logs/")
async def fetch_logs(current_user: User = Depends(get_current_user), db=Depends(get_db)):
    # Retrieve logs for the current user
    user_logs = db.query(LogEntryModel).filter(LogEntryModel.user_id == current_user.user_id).all()
    return [
        {
            "message": log.message,
            "time": log.time,
            "level": log.level
        }
        for log in user_logs
    ]
