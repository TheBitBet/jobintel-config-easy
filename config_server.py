from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml
import re

# Adjust paths if your structure is different
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config" / "default.yml"
EXAMPLES_DIR = BASE_DIR / "config" / "examples"

EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # if you later want to restrict, do it here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConfigPayload(BaseModel):
    pipeline: dict
    sources: dict
    scoring: dict
    storage: dict | None = None
    notify: dict


class SaveRequest(BaseModel):
    filename: str
    config: ConfigPayload


def load_default_config():
    if not DEFAULT_CONFIG_PATH.exists():
        raise RuntimeError(f"Default config not found at {DEFAULT_CONFIG_PATH}")
    with DEFAULT_CONFIG_PATH.open() as f:
        return yaml.safe_load(f)


def safe_filename(name: str) -> str:
    """
    Sanitize filename: allow letters, numbers, dash, underscore only.
    Force .yml extension.
    """
    # Strip extension from user input
    name = name.strip()
    if not name:
        raise ValueError("Filename cannot be empty")

    base = re.sub(r"[^A-Za-z0-9_-]", "_", name)
    if not base:
        raise ValueError("Filename becomes empty after sanitization")

    return f"{base}.yml"


@app.get("/api/config/default")
def get_default_config():
    """
    Returns the current default.yml content.
    You can use it as a starting point in the UI.
    """
    try:
        cfg = load_default_config()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return cfg


@app.post("/api/config/save")
def save_config(req: SaveRequest):
    """
    Save a config under config/examples/<filename>.yml
    """
    try:
        filename = safe_filename(req.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    target_path = EXAMPLES_DIR / filename

    # Convert Pydantic model to plain dict
    cfg_dict = {
        "pipeline": req.config.pipeline,
        "sources": req.config.sources,
        "scoring": req.config.scoring,
    }
    # storage & notify are optional in your use, but we include them if present
    if req.config.storage is not None:
        cfg_dict["storage"] = req.config.storage
    if req.config.notify is not None:
        cfg_dict["notify"] = req.config.notify

    with target_path.open("w") as f:
        yaml.safe_dump(cfg_dict, f, sort_keys=False)

    return {"status": "ok", "path": str(target_path)}
