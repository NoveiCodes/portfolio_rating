from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from database import Base, engine, AsyncSessionLocal
from contextlib import asynccontextmanager
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from routers import feedbacks, users
from sqlalchemy import select
import os
from dotenv import load_dotenv
from models import User


load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn. run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == ADMIN_EMAIL)
        )
        admin_user = result.scalars().first()

        if not admin_user:
            new_admin = User(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                role="admin"
            )
            session.add(new_admin)
            await session.commit()

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(
    feedbacks.router, prefix="/api/feedbacks", tags=["feedbacks"])


@app.get("/", include_in_schema=False)
@app.get("/feedbacks", include_in_schema=False)
def home():
    return f"hehe"


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    return await http_exception_handler(request, exception)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    return await request_validation_exception_handler(request, exception)
