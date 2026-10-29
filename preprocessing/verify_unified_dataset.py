from pathlib import Path
from PIL import Image
import hashlib
import json

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

UNIFIED_DIR = PROJECT_ROOT / "data" / "unified"
SUMMARY_FILE = PROJECT_ROOT / "results" / "unified_dataset_summary.json"
OUTPUT_FILE = PROJECT_ROOT / "results" / "unified_dataset_verification.json"

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}

EXPECTED_CLASSES = {
    "Potato_Early_Blight",
    "Potato_Late_Blight",
    "Potato_Healthy",
    "Tomato_Bacterial_Spot",
    "Tomato_Early_Blight",
    "Tomato_Late_Blight",
    "Tomato_Leaf_Mold",
    "Tomato_Septoria_Leaf_Spot",
    "Tomato_Healthy",
    "Corn_Gray_Leaf_Spot",
    "Corn_Leaf_Blight",
    "Corn_Leaf_Rust",
    "Apple_Healthy",
    "Apple_Rust",
    "Apple_Scab",
    "Potato_Leaf_Blight",
    "Potato_Leafroll_Virus"
}


def calculate_sha256(file_path):
    """Calculate SHA-256 hash."""

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


def main():

    print("=" * 70)
    print("VERIFYING UNIFIED DATASET")
    print("=" * 70)

    if not UNIFIED_DIR.exists():
        raise FileNotFoundError(
            f"Unified dataset not found:\n{UNIFIED_DIR}"
        )

    # ========================================================
    # FIND CLASS DIRECTORIES
    # ========================================================

    class_directories = sorted(
        [
            path for path in UNIFIED_DIR.iterdir()
            if path.is_dir()
        ]
    )

    actual_classes = {
        path.name for path in class_directories
    }

    missing_classes = EXPECTED_CLASSES - actual_classes
    unexpected_classes = actual_classes - EXPECTED_CLASSES

    print("\nExpected classes:", len(EXPECTED_CLASSES))
    print("Found classes:", len(actual_classes))

    if missing_classes:
        print("\nMissing classes:")
        for cls in sorted(missing_classes):
            print("  -", cls)
    else:
        print("All expected classes are present.")

    if unexpected_classes:
        print("\nUnexpected classes:")
        for cls in sorted(unexpected_classes):
            print("  -", cls)

    # ========================================================
    # IMAGE VALIDATION
    # ========================================================

    total_images = 0
    valid_images = 0
    invalid_images = []

    class_counts = {}

    print("\nChecking images...")

    for class_dir in class_directories:

        images = [
            path for path in class_dir.rglob("*")
            if path.is_file()
            and path.suffix.lower() in IMAGE_EXTENSIONS
        ]

        class_counts[class_dir.name] = len(images)
        total_images += len(images)

        for image_path in images:

            try:
                with Image.open(image_path) as img:
                    img.verify()

                valid_images += 1

            except Exception as e:

                invalid_images.append({
                    "file": str(
                        image_path.relative_to(UNIFIED_DIR)
                    ).replace("\\", "/"),
                    "error": str(e)
                })

    # ========================================================
    # DUPLICATE CHECK
    # ========================================================

    print("\nChecking exact duplicates inside unified dataset...")

    hash_to_files = {}

    all_images = [
        path
        for path in UNIFIED_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    ]

    for index, image_path in enumerate(all_images, start=1):

        file_hash = calculate_sha256(image_path)

        hash_to_files.setdefault(
            file_hash,
            []
        ).append(
            str(
                image_path.relative_to(UNIFIED_DIR)
            ).replace("\\", "/")
        )

        if index % 1000 == 0:
            print(
                f"Hashed {index}/{len(all_images)} images..."
            )

    duplicate_groups = [
        files
        for files in hash_to_files.values()
        if len(files) > 1
    ]

    duplicate_file_count = sum(
        len(files)
        for files in duplicate_groups
    )

    # ========================================================
    # LOAD CREATION SUMMARY
    # ========================================================

    creation_summary = None

    if SUMMARY_FILE.exists():

        with open(
            SUMMARY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            creation_summary = json.load(f)

    # ========================================================
    # FINAL RESULT
    # ========================================================

    verification = {
        "expected_class_count": len(EXPECTED_CLASSES),
        "actual_class_count": len(actual_classes),
        "missing_classes": sorted(missing_classes),
        "unexpected_classes": sorted(unexpected_classes),

        "total_images": total_images,
        "valid_images": valid_images,
        "invalid_image_count": len(invalid_images),
        "invalid_images": invalid_images,

        "duplicate_groups": len(duplicate_groups),
        "duplicate_file_count": duplicate_file_count,
        "duplicate_groups_details": duplicate_groups,

        "class_counts": class_counts,

        "verification_status": (
            len(missing_classes) == 0
            and len(unexpected_classes) == 0
            and len(invalid_images) == 0
            and len(duplicate_groups) == 0
        )
    }

    # ========================================================
    # SAVE REPORT
    # ========================================================

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            verification,
            f,
            indent=4
        )

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    print("\n")
    print("=" * 70)
    print("VERIFICATION RESULTS")
    print("=" * 70)

    print(
        f"\nClasses: "
        f"{len(actual_classes)}/{len(EXPECTED_CLASSES)}"
    )

    print(
        f"Total images: "
        f"{total_images}"
    )

    print(
        f"Valid images: "
        f"{valid_images}"
    )

    print(
        f"Invalid images: "
        f"{len(invalid_images)}"
    )

    print(
        f"Exact duplicate groups: "
        f"{len(duplicate_groups)}"
    )

    print(
        f"Files involved in duplicates: "
        f"{duplicate_file_count}"
    )

    print("\nClass-wise counts:")

    for class_name in sorted(class_counts):

        print(
            f"  {class_name}: "
            f"{class_counts[class_name]}"
        )

    print("\nVerification status:")

    if verification["verification_status"]:
        print("PASS - Unified dataset is clean.")
    else:
        print("CHECK REQUIRED - Issues were detected.")

    print("\nReport saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()