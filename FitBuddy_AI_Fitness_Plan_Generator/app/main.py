from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from .database import init_db
from .routes import router

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
load_dotenv(PROJECT_DIR / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="FitBuddy — AI Fitness Plan Generator",
    description="Generate and refine 7-day workout plans with Gemini.",
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "application": "FitBuddy"}
