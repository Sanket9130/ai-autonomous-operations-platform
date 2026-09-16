"""
Model serialization, loading, and metadata utilities.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
import joblib

MODEL_FILENAME = "best_hvac_model.joblib"
METADATA_FILENAME = "model_metadata.json"


def get_models_dir() -> Path:
    """Return absolute path to serialized models directory."""
    models_dir = Path(__file__).resolve().parent.parent.parent / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def save_model(model: Any, filename: str = MODEL_FILENAME) -> Path:
    """Serialize model artifact to disk."""
    path = get_models_dir() / filename
    joblib.dump(model, path)
    return path


def load_model(filename: str = MODEL_FILENAME) -> Optional[Any]:
    """Load serialized model artifact from disk."""
    path = get_models_dir() / filename
    if not path.exists():
        return None
    return joblib.load(path)


def save_metadata(metadata: Dict[str, Any], filename: str = METADATA_FILENAME) -> Path:
    """Save model evaluation metrics and schema metadata to JSON."""
    path = get_models_dir() / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    return path


def load_metadata(filename: str = METADATA_FILENAME) -> Dict[str, Any]:
    """Load model evaluation metadata JSON."""
    path = get_models_dir() / filename
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
