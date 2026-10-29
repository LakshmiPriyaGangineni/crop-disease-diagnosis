from pathlib import Path
from collections import Counter
from PIL import Image
import hashlib


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = PROJECT_DIR / "datasets"

DATASETS = [
    "dataset_1_plantvillage",
    "dataset_2_crops_disease",
    "dataset_6_web_sourced",
]

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff",
}


def get_images(dataset_path):
    """Return all image files inside a dataset."""
    return [
        file
        for file in dataset_path.rglob("*")
        if file.is_file()
        and file.suffix.lower() in IMAGE_EXTENSIONS
    ]


def calculate_hash(file_path):
    """Calculate SHA-256 hash of an image file."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            data = file.read(1024 * 1024)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def analyze_dataset(dataset_name):

    dataset_path = DATASETS_DIR / dataset_name

    print("\n" + "=" * 75)
    print(f"DATASET: {dataset_name}")
    print("=" * 75)

    if not dataset_path.exists():
        print("Dataset not found.")
        return

    images = get_images(dataset_path)

    print(f"\nTotal images: {len(images)}")

    valid_images = 0
    invalid_images = 0

    formats = Counter()
    sizes = Counter()

    hashes = {}
    duplicate_count = 0

    print("\nChecking images...")

    for index, image_path in enumerate(images, start=1):

        # -----------------------------
        # Check image validity
        # -----------------------------

        try:

            with Image.open(image_path) as image:

                image.verify()

            # Re-open after verify()
            with Image.open(image_path) as image:

                width, height = image.size

                formats[image_path.suffix.lower()] += 1
                sizes[(width, height)] += 1

            valid_images += 1

        except Exception as error:

            invalid_images += 1

            print(
                f"\nINVALID IMAGE: "
                f"{image_path.relative_to(dataset_path)}"
            )

            print(f"Reason: {error}")

            continue

        # -----------------------------
        # Duplicate check
        # -----------------------------

        try:

            image_hash = calculate_hash(image_path)

            if image_hash in hashes:

                duplicate_count += 1

            else:

                hashes[image_hash] = image_path

        except Exception:
            pass

        # Progress
        if index % 500 == 0:
            print(f"Checked {index}/{len(images)} images...")

    # -----------------------------
    # Results
    # -----------------------------

    print("\n" + "-" * 75)
    print("RESULTS")
    print("-" * 75)

    print(f"Valid images:   {valid_images}")
    print(f"Invalid images: {invalid_images}")
    print(f"Duplicates:     {duplicate_count}")

    print("\nImage formats:")

    for extension, count in sorted(formats.items()):
        print(f"  {extension}: {count}")

    print("\nMost common image sizes:")

    for size, count in sizes.most_common(10):
        print(f"  {size[0]} x {size[1]} -> {count} images")


# ==========================================================
# MAIN
# ==========================================================

print("=" * 75)
print("CLASSIFICATION DATASET QUALITY CHECK")
print("=" * 75)

print("\nDatasets being checked:")

for dataset in DATASETS:
    print(f"  - {dataset}")

for dataset in DATASETS:
    analyze_dataset(dataset)

print("\n" + "=" * 75)
print("QUALITY CHECK COMPLETED")
print("=" * 75)