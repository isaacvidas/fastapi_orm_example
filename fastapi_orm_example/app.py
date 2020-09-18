from typing import List

import sqltap
import uvicorn
from fastapi import Depends, FastAPI
from starlette.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from . import models, schemas
from .database import SessionLocal, engine

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def reset_db():
    try:
        db = SessionLocal()
        # deleting all items and users
        db.query(models.Item).delete()
        db.query(models.User).delete()

        # Populate users table
        for i in range(50):
            user = models.User(email=f"user{i}@email.com", hashed_password=f"pwdforuser{i}")
            db.add(user)
        db.commit()

        # Populate items table
        users = db.query(models.User).all()
        for user in users:
            for i in range(20):
                user_item = models.Item(title=f"Item{i}", description=f"Item{i} description", owner=user)
                db.add(user_item)
        db.commit()
    finally:
        db.close()


@app.middleware("http")
async def add_sql_tap(request: Request, call_next):
    profiler = sqltap.start()
    response = await call_next(request)
    statistics = profiler.collect()
    sqltap.report(statistics, "report.txt", report_format="text")
    return response


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    # users = db.query(models.User).options(joinedload(models.User.items)).offset(skip).limit(limit).all() # The fix to the N+1 issue
    return users


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
