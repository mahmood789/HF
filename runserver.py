# runserver.py  – small launcher so we don't rely on the uvicorn CLI directly
import uvicorn
from app import app  # FastAPI instance from app.py

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),  # Render sets $PORT automatically
        reload=True,  # enable live-reload (useful during dev)
    )
