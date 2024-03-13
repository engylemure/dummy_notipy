from notipy.utils.db import sessionmanager, redismanager
from notipy.api import user
from contextlib import asynccontextmanager
from fastapi import FastAPI
import sys

running = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()

    if redismanager is not None:
        await redismanager.close()


app = FastAPI(lifespan=lifespan)

app.include_router(user.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
