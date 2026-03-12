from fastapi import FastAPI, Depends
import uvicorn
from db.models import UserRecord
from db.database import Base, engine
from sqlalchemy.orm import Session
from api.routes import core_router, auth_router
from api.lifespan import lifespan

Base.metadata.create_all(bind=engine)

app = FastAPI(lifespan = lifespan)

app.include_router(core_router)
app.include_router(auth_router)

# ----------------------------------------
def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
