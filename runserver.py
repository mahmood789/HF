# runserver.py – Launcher to start the FastAPI app without relying on uvicorn CLI

import os
import uvicorn
from app import app

if __name__=="__main__":
  uvicorn.run(
    app,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8080)),
    reload=True  # Enable hot-reload during development
  )
