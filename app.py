"""
EchoSim – flat-repo FastAPI entrypoint.
Serves static SVG, routes, and custom OpenAPI spec.
"""
from pathlib import Path
import json
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import router

BASE = Path(__file__).parent

app = FastAPI(title="EchoSim")

# expose banner_template.svg (and any other assets) at /static/*
app.mount("/static", StaticFiles(directory=BASE), name="static")

# API endpoints
app.include_router(router)

# serve hand-written OpenAPI spec
@app.get("/openapi.json", include_in_schema=False)
def custom_spec():
    return json.loads(Path("openapi_schema.json").read_text())

@app.get("/", include_in_schema=False)
def root():
    return {"detail": "EchoSim flat-repo server running"}
