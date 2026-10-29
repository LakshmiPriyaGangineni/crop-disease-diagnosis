import os
import shutil
import random
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_DIR = Path("data/unified_clean")

TRAIN_DIR = Path("data/unified_train")
VAL_DIR = Path("data/unified_validation")
TEST_DIR = Path("data/unified_test")

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

RANDOM_SEED = 42

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}


# ============================================================
# SET RANDOM SEED
# ============================================================

random.seed(RANDOM_SEED)


# ============================================================
# CHECK SOURCE DATASET
# ============================================================

if not SOURCE_DIR.exists():
    raise FileNotFoundError(
        f"Source dataset not found: {SOURCE_DIR}"
    )


# ============================================================
# CREATE OUTPUT DIRECTORIES
# ============================================================

for directory in [TRAIN_DIR, VAL_DIR, TEST_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# GET CLASS FOLDERS
# ============================================================

class_folders = sorted(
    [folder for folder in SOURCE_DIR.iterdir() if folder.is_dir()]
)

print("=" * 70)
print("SPLITTING CLEAN UNIFIED DATASET")
print("=" * 70)

print(f"\nSource: {SOURCE_DIR}")
print(f"Number of classes: {len(class_folders)}")
print("Split: 70% Train / 15% Validation / 15% Test")
print(f"Random seed: {RANDOM_SEED}\n")


# ============================================================
# SPLIT EACH CLASS
# ============================================================

total_images = 0
total_train = 0
total_val = 0
total_test = 0

for class_folder in class_folders:

    class_name = class_folder.name

    images = [
        file for file in class_folder.iterdir()
        if file.is_file() and file.suffix in IMAGE_EXTENSIONS
    ]

    # Shuffle images
    random.shuffle(images)

    total = len(images)

    # Calculate split sizes
    train_count = int(total * TRAIN_RATIO)
    val_count = int(total * VAL_RATIO)

    # Remaining images go to test
    test_count = total - train_count - val_count

    train_images = images[:train_count]
    val_images = images[train_count:train_count + val_count]
    test_images = images[train_count + val_count:]

    # Create class directories
    train_class_dir = TRAIN_DIR / class_name
    val_class_dir = VAL_DIR / class_name
    test_class_dir = TEST_DIR / class_name

    train_class_dir.mkdir(parents=True, exist_ok=True)
    val_class_dir.mkdir(parents=True, exist_ok=True)
    test_class_dir.mkdir(parents=True, exist_ok=True)

    # Copy training images
    for image in train_images:
        shutil.copy2(image, train_class_dir / image.name)

    # Copy validation images
    for image in val_images:
        shutil.copy2(image, val_class_dir / image.name)

    # Copy test images
    for image in test_images:
        shutil.copy2(image, test_class_dir / image.name)

    total_images += total
    total_train += train_count
    total_val += val_count
    total_test += test_count

    print(
        f"{class_name}: "
        f"Total={total}, "
        f"Train={train_count}, "
        f"Val={val_count}, "
        f"Test={test_count}"
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SPLIT COMPLETE")
print("=" * 70)

print(f"\nTotal images:       {total_images}")
print(f"Training images:    {total_train}")
print(f"Validation images:  {total_val}")
print(f"Test images:        {total_test}")

print("\nCreated folders:")
print(f"  {TRAIN_DIR}")
print(f"  {VAL_DIR}")
print(f"  {TEST_DIR}")

print("\nOriginal cleaned dataset was NOT modified.")
print("=" * 70)