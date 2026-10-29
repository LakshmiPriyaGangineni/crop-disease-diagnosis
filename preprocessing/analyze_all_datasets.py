from pathlib import Path
from collections import Counter

# Project root
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = PROJECT_DIR / "datasets"

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"
}


def analyze_dataset(dataset_path):
    print("\n" + "=" * 70)
    print(f"DATASET: {dataset_path.name}")
    print("=" * 70)

    if not dataset_path.exists():
        print("Dataset folder not found.")
        return

    total_images = 0
    extensions = Counter()
    folders_with_images = []

    # Scan all files recursively
    for file in dataset_path.rglob("*"):

        if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS:
            total_images += 1
            extensions[file.suffix.lower()] += 1

    # Find folders that directly contain images
    for folder in dataset_path.rglob("*"):

        if folder.is_dir():
            image_count = sum(
                1
                for file in folder.iterdir()
                if file.is_file()
                and file.suffix.lower() in IMAGE_EXTENSIONS
            )

            if image_count > 0:
                folders_with_images.append(
                    (folder.relative_to(dataset_path), image_count)
                )

    print(f"\nTotal images: {total_images}")

    print("\nImage formats:")
    for ext, count in sorted(extensions.items()):
        print(f"  {ext}: {count}")

    print("\nFolders containing images:")

    if folders_with_images:
        for folder, count in sorted(folders_with_images):
            print(f"  {folder} -> {count} images")
    else:
        print("  No image-containing folders found.")

    print(f"\nNumber of image-containing folders: {len(folders_with_images)}")


# --------------------------------------------------
# Analyze all 6 datasets
# --------------------------------------------------

print("=" * 70)
print("CROP DISEASE DATASET ANALYSIS")
print("=" * 70)

if not DATASETS_DIR.exists():
    print(f"\nERROR: Dataset directory not found:")
    print(DATASETS_DIR)
    raise SystemExit

datasets = sorted(
    folder for folder in DATASETS_DIR.iterdir()
    if folder.is_dir()
)

print(f"\nDatasets found: {len(datasets)}")

for dataset in datasets:
    analyze_dataset(dataset)

print("\n" + "=" * 70)
print("ANALYSIS COMPLETED")
print("=" * 70)