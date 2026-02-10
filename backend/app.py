from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import router
from models.database import Database
import uvicorn
import os
import traceback

# Load environment variables if needed
from dotenv import load_dotenv
load_dotenv()

# FastAPI app
app = FastAPI(
    title="Farm AI Assistant",
    description="Multi-Agent AI system for traditional & greenhouse farmers",
    version="0.1.1",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - MUST be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler to ensure CORS headers on errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Include API routes
app.include_router(router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Farm AI Assistant API",
        "status": "running",
        "version": "0.1.1",
        "docs": "/docs",
        "health": "/health",
        "api": "/api"
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Lifespan events
@app.on_event("startup")
async def startup_event():
    print("Starting Farm AI Assistant backend...")
    try:
        await Database.connect_db()
    except Exception as e:
        print(f"MongoDB connection warning: {e}")
        print("Continuing without MongoDB - will retry on first request")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down Farm AI Assistant backend...")
    await Database.close_db()

# Run app
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
