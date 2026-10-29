import os
from collections import Counter
from PIL import Image

# Path to your PlantVillage dataset
DATASET_PATH = "PlantVillage"

# Supported image formats
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

class_counts = Counter()
total_images = 0
invalid_images = 0

print("=" * 60)
print("PLANTVILLAGE DATASET ANALYSIS")
print("=" * 60)

# Check dataset path
if not os.path.exists(DATASET_PATH):
    print(f"Dataset not found: {DATASET_PATH}")
    exit()

# Go through class folders
for class_name in sorted(os.listdir(DATASET_PATH)):

    class_path = os.path.join(DATASET_PATH, class_name)

    if not os.path.isdir(class_path):
        continue

    count = 0

    for file_name in os.listdir(class_path):

        file_path = os.path.join(class_path, file_name)

        extension = os.path.splitext(file_name)[1].lower()

        if extension in IMAGE_EXTENSIONS:

            try:
                with Image.open(file_path) as img:
                    img.verify()

                count += 1
                total_images += 1

            except Exception:
                invalid_images += 1

    class_counts[class_name] = count


# Display results
print("\nNumber of classes:", len(class_counts))
print("Total images:", total_images)
print("Invalid images:", invalid_images)

print("\nImages per class:")
print("-" * 60)

for class_name, count in class_counts.items():
    print(f"{class_name:<45} {count}")

print("=" * 60)
print("Dataset analysis completed.")
print("=" * 60)