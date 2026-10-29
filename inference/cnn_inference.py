"""
CNN inference for crop disease prediction.

Loads the trained CropDiseaseCNN checkpoint (models/best_model.pth) and
predicts the disease class for a single leaf image.

Preprocessing is identical to `val_transform` in training/train_cnn.py:
    Resize((256, 256)) -> ToTensor() -> Normalize(ImageNet mean/std)

Class order comes from the checkpoint's "classes" list (the exact
ImageFolder ordering used at training time) and is cross-checked against
results/class_mapping.json.
"""

import json
import os
import sys

import torch
import torch.nn.functional as F
from PIL import Image, UnidentifiedImageError
from torchvision import transforms

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Reuse the exact training architecture (read-only import).
_TRAINING_DIR = os.path.join(PROJECT_ROOT, "training")
if _TRAINING_DIR not in sys.path:
    sys.path.insert(0, _TRAINING_DIR)

from cnn_model import CropDiseaseCNN  # noqa: E402

MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "best_model.pth")
CLASS_MAPPING_PATH = os.path.join(PROJECT_ROOT, "results", "class_mapping.json")

# Values copied from training/train_cnn.py (val_transform).
IMAGE_SIZE = 256
NORM_MEAN = [0.485, 0.456, 0.406]
NORM_STD = [0.229, 0.224, 0.225]

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

TRANSFORM = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=NORM_MEAN, std=NORM_STD),
])

_cache = {}


class ModelLoadError(RuntimeError):
    """Raised when the checkpoint or class mapping cannot be loaded."""


class InvalidImageError(ValueError):
    """Raised when the image path is missing or not a readable image."""


def _load_class_mapping_keys():
    try:
        with open(CLASS_MAPPING_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f).keys())
    except (OSError, json.JSONDecodeError) as exc:
        raise ModelLoadError(
            f"Could not read class mapping file '{CLASS_MAPPING_PATH}': {exc}"
        ) from exc


def load_model(model_path=MODEL_PATH, force_reload=False):
    """Load model and class list. Returns (model, classes). Cached."""
    if not force_reload and "model" in _cache and _cache.get("path") == model_path:
        return _cache["model"], _cache["classes"]

    if not os.path.isfile(model_path):
        raise ModelLoadError(f"Model checkpoint not found: {model_path}")

    try:
        checkpoint = torch.load(model_path, map_location=DEVICE)
    except Exception as exc:
        raise ModelLoadError(
            f"Failed to read checkpoint '{model_path}': {exc}"
        ) from exc

    if (
        not isinstance(checkpoint, dict)
        or "model_state_dict" not in checkpoint
        or "classes" not in checkpoint
    ):
        raise ModelLoadError(
            "Unexpected checkpoint format. Expected a dict with keys "
            "'model_state_dict' and 'classes'."
        )

    classes = list(checkpoint["classes"])

    # Validate class list against results/class_mapping.json.
    mapping_keys = _load_class_mapping_keys()
    if set(classes) != mapping_keys:
        raise ModelLoadError(
            "Checkpoint classes do not match results/class_mapping.json. "
            f"Only in checkpoint: {sorted(set(classes) - mapping_keys)}; "
            f"only in mapping: {sorted(mapping_keys - set(classes))}"
        )

    try:
        model = CropDiseaseCNN(num_classes=len(classes))
        model.load_state_dict(checkpoint["model_state_dict"])
    except Exception as exc:
        raise ModelLoadError(
            f"Checkpoint weights do not match CropDiseaseCNN architecture: {exc}"
        ) from exc

    model.to(DEVICE)
    model.eval()

    _cache.update(model=model, classes=classes, path=model_path)
    return model, classes


def predict_image(image_input, top_k=3):
    """
    Predict the disease for a single leaf image.
    Supports file paths, file-like objects (streams), and PIL Images.

    Returns:
        {
            "predicted_class": str,
            "confidence": float (0-1),
            "class_index": int,
            "top3": [{"class": str, "class_index": int, "probability": float}, ...]
        }
    """
    if isinstance(image_input, Image.Image):
        image = image_input.convert("RGB")
    elif hasattr(image_input, "read"):
        try:
            if hasattr(image_input, "seek"):
                try:
                    image_input.seek(0)
                except Exception:
                    pass
            with Image.open(image_input) as img:
                image = img.convert("RGB")
        except (UnidentifiedImageError, OSError, Exception) as exc:
            raise InvalidImageError(
                f"Could not open image: {exc}"
            ) from exc
    elif isinstance(image_input, (str, os.PathLike)):
        image_path = os.fspath(image_input)
        if not str(image_path).strip():
            raise InvalidImageError("image_path must be a non-empty path string.")

        if not os.path.exists(image_path):
            raise InvalidImageError(f"Image file not found: {image_path}")
        if not os.path.isfile(image_path):
            raise InvalidImageError(f"Path is not a file: {image_path}")

        try:
            with Image.open(image_path) as img:
                image = img.convert("RGB")
        except (UnidentifiedImageError, OSError) as exc:
            raise InvalidImageError(
                f"Could not open '{image_path}' as an image: {exc}"
            ) from exc
    else:
        raise InvalidImageError("image_input must be a path string, file-like object, or PIL Image.")

    model, classes = load_model()

    tensor = TRANSFORM(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(tensor)
        probs = F.softmax(logits, dim=1).squeeze(0)

    k = min(top_k, len(classes))
    top_probs, top_idx = torch.topk(probs, k)

    top = [
        {
            "class": classes[i],
            "class_index": int(i),
            "probability": round(float(p), 6),
        }
        for p, i in zip(top_probs.tolist(), top_idx.tolist())
    ]

    top_confidence = top[0]["probability"]
    is_uncertain = top_confidence < 0.50

    warning = None
    if is_uncertain:
        warning = (
            f"Visual diagnosis is uncertain ({top_confidence * 100:.1f}% < 50.0%). "
            "The model could not distinguish a single class with high certainty. "
            "Review top candidate alternatives before taking action."
        )

    return {
        "predicted_class": top[0]["class"],
        "confidence": top[0]["probability"],
        "class_index": top[0]["class_index"],
        "top3": top,
        "uncertain": is_uncertain,
        "warning": warning,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m inference.cnn_inference <image_path>")
        sys.exit(1)
    print(json.dumps(predict_image(sys.argv[1]), indent=2))
