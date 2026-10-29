from pathlib import Path
import hashlib
from collections import defaultdict

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = PROJECT_DIR / "datasets"

DATASETS = [
    "dataset_1_plantvillage",
    "dataset_2_crops_disease",
    "dataset_6_web_sourced",
]

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"
}


def get_images(dataset_path):
    return [
        file for file in dataset_path.rglob("*")
        if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS
    ]


def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            data = file.read(1024 * 1024)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


print("=" * 75)
print("CROSS-DATASET DUPLICATE CHECK")
print("=" * 75)

# Store hash -> dataset and file information
hash_map = defaultdict(list)

# Process each dataset
for dataset_name in DATASETS:

    dataset_path = DATASETS_DIR / dataset_name

    print(f"\nProcessing: {dataset_name}")

    if not dataset_path.exists():
        print("Dataset not found.")
        continue

    images = get_images(dataset_path)

    print(f"Images found: {len(images)}")

    for index, image_path in enumerate(images, start=1):

        try:
            image_hash = calculate_hash(image_path)

            hash_map[image_hash].append(
                (dataset_name, image_path)
            )

        except Exception as error:
            print(f"Error: {image_path}")
            print(f"Reason: {error}")

        if index % 500 == 0:
            print(f"Processed {index}/{len(images)} images...")


# Find hashes that occur in more than one dataset
cross_dataset_duplicates = []

for image_hash, files in hash_map.items():

    datasets_found = set(
        dataset_name for dataset_name, _ in files
    )

    if len(datasets_found) > 1:
        cross_dataset_duplicates.append(
            (image_hash, files)
        )


print("\n" + "=" * 75)
print("CROSS-DATASET DUPLICATE RESULTS")
print("=" * 75)

if not cross_dataset_duplicates:

    print("\nNo exact duplicate images were found between datasets.")

else:

    print(
        f"\nExact duplicate image groups found across datasets: "
        f"{len(cross_dataset_duplicates)}"
    )

    for group_number, (image_hash, files) in enumerate(
        cross_dataset_duplicates, start=1
    ):

        print("\n" + "-" * 75)
        print(f"DUPLICATE GROUP {group_number}")
        print("-" * 75)

        for dataset_name, image_path in files:

            relative_path = image_path.relative_to(
                DATASETS_DIR / dataset_name
            )

            print(f"Dataset : {dataset_name}")
            print(f"File    : {relative_path}")

# Summary by dataset pair
pair_counts = defaultdict(int)

for image_hash, files in cross_dataset_duplicates:

    datasets_found = sorted(
        set(dataset_name for dataset_name, _ in files)
    )

    for i in range(len(datasets_found)):
        for j in range(i + 1, len(datasets_found)):

            pair = (
                datasets_found[i],
                datasets_found[j]
            )

            pair_counts[pair] += 1


print("\n" + "=" * 75)
print("DUPLICATE SUMMARY BY DATASET PAIR")
print("=" * 75)

if pair_counts:

    for pair, count in pair_counts.items():

        print(
            f"{pair[0]} <--> {pair[1]} : "
            f"{count} duplicate groups"
        )

else:

    print("\nNo cross-dataset duplicates found.")

print("\n" + "=" * 75)
print("CROSS-DATASET CHECK COMPLETED")
print("=" * 75)