from pathlib import Path
import hashlib
import json

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Raw dataset locations
D1_DIR = PROJECT_ROOT / "datasets" / "dataset_1_plantvillage"
D2_DIR = PROJECT_ROOT / "datasets" / "dataset_2_crops_disease"

# Output file
OUTPUT_FILE = PROJECT_ROOT / "results" / "cross_dataset_duplicates.json"

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


def calculate_sha256(file_path):
    """Calculate SHA-256 hash of an image file."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


def collect_images(dataset_dir):
    """Collect all image files recursively."""
    images = []

    for file_path in dataset_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(file_path)

    return images


def build_hash_index(image_files):
    """Create hash -> file paths mapping."""
    hash_index = {}

    for i, file_path in enumerate(image_files, start=1):
        file_hash = calculate_sha256(file_path)

        hash_index.setdefault(file_hash, []).append(file_path)

        if i % 500 == 0:
            print(f"Processed {i}/{len(image_files)} images...")

    return hash_index


def main():

    print("=" * 60)
    print("CREATING CROSS-DATASET DUPLICATE EXCLUSION LIST")
    print("=" * 60)

    print("\nCollecting Dataset 1 images...")
    d1_images = collect_images(D1_DIR)
    print(f"Dataset 1 images: {len(d1_images)}")

    print("\nCollecting Dataset 2 images...")
    d2_images = collect_images(D2_DIR)
    print(f"Dataset 2 images: {len(d2_images)}")

    print("\nCalculating Dataset 1 hashes...")
    d1_hashes = build_hash_index(d1_images)

    print("\nCalculating Dataset 2 hashes...")
    d2_hashes = build_hash_index(d2_images)

    print("\nFinding exact duplicates...")

    duplicate_groups = []

    common_hashes = set(d1_hashes.keys()) & set(d2_hashes.keys())

    for file_hash in sorted(common_hashes):

        for d1_file in d1_hashes[file_hash]:
            for d2_file in d2_hashes[file_hash]:

                duplicate_groups.append({
                    "sha256": file_hash,
                    "dataset_1": str(d1_file.relative_to(D1_DIR)),
                    "dataset_2": str(d2_file.relative_to(D2_DIR))
                })

    # Create results directory if needed
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "description": "Confirmed exact duplicate images between Dataset 1 and Dataset 2",
        "dataset_1": "dataset_1_plantvillage",
        "dataset_2": "dataset_2_crops_disease",
        "duplicate_count": len(duplicate_groups),
        "duplicates": duplicate_groups
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)

    print(f"Exact duplicate groups found: {len(duplicate_groups)}")
    print(f"Output file: {OUTPUT_FILE}")

    if len(duplicate_groups) == 150:
        print("\nSUCCESS: 150 confirmed duplicates found.")
    else:
        print(
            f"\nWARNING: Expected 150 duplicates, "
            f"but found {len(duplicate_groups)}."
        )

    print("\nRaw datasets were NOT modified.")


if __name__ == "__main__":
    main()