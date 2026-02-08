"""
Meeting Notes API - FastAPI Backend

Main application entry point.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
print("🚀 BACKEND MAIN STARTING...")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db
from backend.routes.auth import router as auth_router
from backend.routes.settings import router as settings_router
from backend.routes.meetings import router as meetings_router
from backend.routes.ask import router as ask_router

# Create app
app = FastAPI(
    title="Meeting Notes API",
    description="Convert meetings to tasks with Notion & Slack integration",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth_router)
app.include_router(settings_router)
app.include_router(meetings_router)
app.include_router(ask_router)

# Serve frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
def root():
    """Serve frontend or API info."""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "Meeting Notes API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_db()
    print("✅ Database initialized")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
