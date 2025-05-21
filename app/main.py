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

# Set up CORS - ONCE, not twice
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Allow localhost:3000 and any origin for development
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

# Include routers - ONCE, not twice
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

# Add health check endpoint - ONCE, not twice
@app.get("/health", status_code=200)
def health_check():
    return {"status": "healthy"}

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to Sentinel API"}

# Startup event to create tables
@app.on_event("startup")
def on_startup():
    try:
        # Import models to register with SQLAlchemy
        # Make sure your file is named alert.py (singular), not alerts.py (plural)
        from .models import user, activity
        from .models.alert import Alert  # Import Alert directly
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Error during startup: {e}")