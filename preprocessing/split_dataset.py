import os
import shutil
import random

SOURCE_DIR = "PlantVillage"
OUTPUT_DIR = "data"

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

random.seed(42)

# Create output folders
for split in ["train", "validation", "test"]:
    os.makedirs(os.path.join(OUTPUT_DIR, split), exist_ok=True)

# Get class folders
classes = [
    folder for folder in os.listdir(SOURCE_DIR)
    if os.path.isdir(os.path.join(SOURCE_DIR, folder))
]

print(f"Found {len(classes)} classes.")

total_images = 0

for class_name in sorted(classes):

    class_path = os.path.join(SOURCE_DIR, class_name)

    images = [
        file for file in os.listdir(class_path)
        if file.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    random.shuffle(images)

    total = len(images)

    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    train_images = images[:train_end]
    val_images = images[train_end:val_end]
    test_images = images[val_end:]

    # Create class folders
    for split in ["train", "validation", "test"]:
        os.makedirs(
            os.path.join(OUTPUT_DIR, split, class_name),
            exist_ok=True
        )

    # Copy images
    for image in train_images:
        shutil.copy2(
            os.path.join(class_path, image),
            os.path.join(OUTPUT_DIR, "train", class_name, image)
        )

    for image in val_images:
        shutil.copy2(
            os.path.join(class_path, image),
            os.path.join(OUTPUT_DIR, "validation", class_name, image)
        )

    for image in test_images:
        shutil.copy2(
            os.path.join(class_path, image),
            os.path.join(OUTPUT_DIR, "test", class_name, image)
        )

    print(
        f"{class_name}: "
        f"Train={len(train_images)}, "
        f"Validation={len(val_images)}, "
        f"Test={len(test_images)}"
    )

    total_images += total

print("\nDataset splitting completed!")
print(f"Total images processed: {total_images}")