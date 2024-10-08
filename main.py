import asyncio
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.routes import contacts, auth, users
from src.conf.config import config

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Redis connection
    r = redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
        decode_responses=True
    )
    await FastAPILimiter.init(r)
    yield
    # Shutdown: Close Redis connection
    await r.close()

app = FastAPI(lifespan=lifespan)

# CORS Middleware setup
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")

@app.get("/")
def index():
    """Root endpoint to check if the application is running."""
    return {"message": "Welcome to FastAPI!"}

@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """Health check endpoint to verify the database connection."""
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() != 1:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Database connection is healthy!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to the database: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
