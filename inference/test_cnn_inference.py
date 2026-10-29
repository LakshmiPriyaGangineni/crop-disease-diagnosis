"""
Sample inference test for the CNN inference module.

NOTE: This is a SAMPLE inference test (one image per class, read-only).
It is NOT the final test-set evaluation.

Run from project root:  python -m inference.test_cnn_inference
"""

import os
import random
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import torch  # noqa: E402

from inference import cnn_inference as ci  # noqa: E402

TEST_DIR = os.path.join(PROJECT_ROOT, "data", "unified_test")
IMAGE_EXTS = (".jpg", ".jpeg", ".png")
SEED = 42


def verify_checkpoint():
    print("=" * 70)
    print("CHECKPOINT COMPATIBILITY CHECK")
    print("=" * 70)

    model, classes = ci.load_model()
    print(f"[OK] Loaded {ci.MODEL_PATH}")
    print(f"     Device: {ci.DEVICE}")

    out_features = model.classifier[-1].out_features
    mapping_keys = ci._load_class_mapping_keys()

    assert out_features == len(classes), "Output layer != checkpoint classes"
    assert len(classes) == len(mapping_keys), "Classes != class_mapping.json size"
    assert set(classes) == mapping_keys, "Class names differ from class_mapping.json"
    print(f"[OK] Output classes: {out_features} == class_mapping.json: {len(mapping_keys)}")
    print("[OK] Checkpoint class names match class_mapping.json")

    test_classes = sorted(
        d for d in os.listdir(TEST_DIR) if os.path.isdir(os.path.join(TEST_DIR, d))
    )
    assert test_classes == classes, "Test folder classes != checkpoint class order"
    print("[OK] Test dataset folders match checkpoint class order")

    # Strict load already verified architecture; confirm param shapes explicitly.
    from cnn_model import CropDiseaseCNN
    ref = CropDiseaseCNN(num_classes=len(classes))
    ref_shapes = {k: tuple(v.shape) for k, v in ref.state_dict().items()}
    ckpt_shapes = {k: tuple(v.shape) for k, v in model.state_dict().items()}
    assert ref_shapes == ckpt_shapes, "Architecture mismatch"
    print("[OK] State-dict keys/shapes match CropDiseaseCNN (strict load)")
    return classes


def pick_sample_images(classes):
    rng = random.Random(SEED)
    samples = []
    for cls in classes:
        folder = os.path.join(TEST_DIR, cls)
        files = sorted(f for f in os.listdir(folder) if f.lower().endswith(IMAGE_EXTS))
        if files:
            samples.append((os.path.join(folder, rng.choice(files)), cls))
    return samples


def test_error_handling():
    print("\n" + "=" * 70)
    print("ERROR HANDLING CHECK")
    print("=" * 70)
    for bad in ["does_not_exist.jpg", "", PROJECT_ROOT, os.path.join(PROJECT_ROOT, ".env")]:
        try:
            ci.predict_image(bad)
            print(f"[FAIL] No error for: {bad!r}")
        except ci.InvalidImageError as exc:
            print(f"[OK] {bad!r} -> InvalidImageError: {exc}")

    try:
        ci.load_model(model_path=os.path.join(PROJECT_ROOT, "models", "missing.pth"),
                      force_reload=True)
        print("[FAIL] No error for missing checkpoint")
    except ci.ModelLoadError as exc:
        print(f"[OK] Missing checkpoint -> ModelLoadError: {exc}")
    finally:
        ci._cache.clear()


def main():
    classes = verify_checkpoint()
    samples = pick_sample_images(classes)

    print("\n" + "=" * 70)
    print("SAMPLE INFERENCE TEST (NOT the final test-set evaluation)")
    print("=" * 70)

    correct = 0
    for path, actual in samples:
        with torch.no_grad():
            result = ci.predict_image(path)
        ok = result["predicted_class"] == actual
        correct += ok
        rel = os.path.relpath(path, PROJECT_ROOT)
        print(f"\nImage     : {rel}")
        print(f"Actual    : {actual}")
        print(f"Predicted : {result['predicted_class']} (index {result['class_index']})")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Correct   : {'YES' if ok else 'NO'}")
        print("Top-3     : " + ", ".join(
            f"{t['class']}={t['probability']:.3f}" for t in result["top3"]))

    total = len(samples)
    print("\n" + "-" * 70)
    print("SAMPLE INFERENCE SUMMARY (sample only, not full test-set accuracy)")
    print(f"Images tested : {total}")
    print(f"Correct       : {correct}")
    print(f"Sample acc.   : {100 * correct / total:.2f}%")
    print("-" * 70)

    test_error_handling()


if __name__ == "__main__":
    main()
