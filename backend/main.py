import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import database, models
from api import router as api_router
import logging

# Setup environment variables
load_dotenv()

# Initialize DB
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Plan Deeper API")

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Plan Deeper API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
