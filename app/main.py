from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from .core.config import settings
from .routes import users, auth, activities, dashboard
from .database import Base, engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sentinel API",
    description="Security monitoring and threat detection API",
    version="0.1.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request timing
class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

app.add_middleware(ProcessTimeMiddleware)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}",
    tags=["authentication"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["users"]
)

app.include_router(
    activities.router, 
    prefix=f"{settings.API_V1_STR}/activities",
    tags=["activities"]
)

app.include_router(
    dashboard.router,
    prefix=f"{settings.API_V1_STR}/dashboard",
    tags=["dashboard"]
)

# Add health check endpoint with correct return value
@app.get("/health", status_code=200)
def health_check():
    return {"status": "healthy"}  # Changed from "ok" to "healthy"

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to Sentinel API"}

# Startup event to create tables
@app.on_event("startup")
def on_startup():
    # Import models here to make sure they're registered with SQLAlchemy
    from .models import user, activity
    
    # Create tables directly
    Base.metadata.create_all(bind=engine)
    logger.info("Application startup complete")

@app.get("/health", status_code=200)
def health_check():
    return {"status": "healthy"}  # Changed from "ok" to "healthy"