from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
import uvicorn
import os

# Load environment variables if needed
from dotenv import load_dotenv
load_dotenv()

# FastAPI app
app = FastAPI(
    title="Farm AI Assistant",
    description="Multi-Agent AI system for traditional & greenhouse farmers",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Lifespan events
@app.on_event("startup")
async def startup_event():
    print("Starting Farm AI Assistant backend...")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down Farm AI Assistant backend...")

# Run app
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
