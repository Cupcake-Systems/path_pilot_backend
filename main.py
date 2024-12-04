import json
import os

from fastapi import FastAPI, Depends

from auth import get_current_user
from data_types import User, LogEntry

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.user_id}


@app.post("/logs/submit")
async def submit_log(log_submission: list[LogEntry], current_user: User = Depends(get_current_user)):
    submitted_logs_count = len(os.listdir("submitted_logs"))
    with open(f"submitted_logs/log{submitted_logs_count + 1}.json", "w") as f:
        json.dump([s.model_dump() for s in log_submission], f)
