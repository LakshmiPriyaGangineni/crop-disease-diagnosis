from pathlib import Path
from PIL import Image
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

HASH_SIZE = 16
HAMMING_THRESHOLD = 8


def get_images(dataset_path):
    return [
        file for file in dataset_path.rglob("*")
        if file.is_file()
        and file.suffix.lower() in IMAGE_EXTENSIONS
    ]


def average_hash(image_path):
    with Image.open(image_path) as image:
        image = image.convert("L")
        image = image.resize((HASH_SIZE, HASH_SIZE))

        pixels = list(image.getdata())
        average = sum(pixels) / len(pixels)

        return "".join(
            "1" if pixel >= average else "0"
            for pixel in pixels
        )


def hamming_distance(hash1, hash2):
    return sum(
        a != b
        for a, b in zip(hash1, hash2)
    )


def get_bucket(image_hash):
    """
    Divide the hash into chunks.
    Similar images are likely to share at least
    one bucket.
    """

    chunk_size = len(image_hash) // 4

    return [
        image_hash[i:i + chunk_size]
        for i in range(0, len(image_hash), chunk_size)
    ]


print("=" * 75)
print("FAST CROSS-DATASET NEAR-DUPLICATE CHECK")
print("=" * 75)


# ---------------------------------------------------------
# STEP 1: CREATE PERCEPTUAL HASHES
# ---------------------------------------------------------

dataset_hashes = {}

for dataset_name in DATASETS:

    dataset_path = DATASETS_DIR / dataset_name

    print(f"\nProcessing: {dataset_name}")

    if not dataset_path.exists():
        print("Dataset not found.")
        continue

    images = get_images(dataset_path)

    print(f"Images found: {len(images)}")

    hashes = []

    for index, image_path in enumerate(images, start=1):

        try:
            image_hash = average_hash(image_path)

            hashes.append(
                (image_hash, image_path)
            )

        except Exception as error:
            print(f"\nError: {image_path}")
            print(f"Reason: {error}")

        if index % 500 == 0:
            print(
                f"Processed {index}/{len(images)} images..."
            )

    dataset_hashes[dataset_name] = hashes


# ---------------------------------------------------------
# STEP 2: COMPARE DATASET PAIRS
# ---------------------------------------------------------

dataset_pairs = [
    (
        "dataset_1_plantvillage",
        "dataset_2_crops_disease"
    ),
    (
        "dataset_1_plantvillage",
        "dataset_6_web_sourced"
    ),
    (
        "dataset_2_crops_disease",
        "dataset_6_web_sourced"
    ),
]


all_results = {}


for dataset1, dataset2 in dataset_pairs:

    print("\n" + "=" * 75)

    print(
        f"Comparing:\n"
        f"  {dataset1}\n"
        f"  {dataset2}"
    )

    print("=" * 75)

    hashes1 = dataset_hashes.get(dataset1, [])
    hashes2 = dataset_hashes.get(dataset2, [])

    # Create buckets for dataset 2
    buckets = defaultdict(list)

    for hash2, image2 in hashes2:

        for bucket in get_bucket(hash2):

            buckets[bucket].append(
                (hash2, image2)
            )

    matches = []

    checked = 0

    for hash1, image1 in hashes1:

        candidates = set()

        # Only compare against images
        # sharing at least one bucket.
        for bucket in get_bucket(hash1):

            for hash2, image2 in buckets.get(
                bucket, []
            ):

                candidates.add(
                    (hash2, image2)
                )

        best_distance = None
        best_image = None

        for hash2, image2 in candidates:

            distance = hamming_distance(
                hash1,
                hash2
            )

            if (
                best_distance is None
                or distance < best_distance
            ):
                best_distance = distance
                best_image = image2

        if (
            best_distance is not None
            and best_distance <= HAMMING_THRESHOLD
        ):

            matches.append(
                (
                    image1,
                    best_image,
                    best_distance
                )
            )

        checked += 1

        if checked % 500 == 0:

            print(
                f"Compared {checked}/{len(hashes1)} images..."
            )

    all_results[
        (dataset1, dataset2)
    ] = matches

    print(
        f"\nNear-duplicate candidates: "
        f"{len(matches)}"
    )


# ---------------------------------------------------------
# STEP 3: DISPLAY RESULTS
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("NEAR-DUPLICATE RESULTS")
print("=" * 75)


total_matches = 0


for (dataset1, dataset2), matches in all_results.items():

    print("\n" + "-" * 75)

    print(
        f"{dataset1} <--> {dataset2}"
    )

    print("-" * 75)

    print(
        f"Near-duplicate candidates: "
        f"{len(matches)}"
    )

    total_matches += len(matches)

    # Display first 20 candidates only
    for index, (
        image1,
        image2,
        distance
    ) in enumerate(matches[:20], start=1):

        relative1 = image1.relative_to(
            DATASETS_DIR / dataset1
        )

        relative2 = image2.relative_to(
            DATASETS_DIR / dataset2
        )

        print(f"\nCandidate {index}")
        print(f"Hamming distance: {distance}")
        print(f"{dataset1}: {relative1}")
        print(f"{dataset2}: {relative2}")

    if len(matches) > 20:

        print(
            f"\n... and "
            f"{len(matches) - 20} more candidates."
        )


# ---------------------------------------------------------
# FINAL SUMMARY
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("FINAL SUMMARY")
print("=" * 75)

print(
    f"\nTotal near-duplicate candidates: "
    f"{total_matches}"
)

print(
    f"\nHamming threshold: "
    f"{HAMMING_THRESHOLD}"
)

print(
    "\nIMPORTANT:"
    "\nThese are similarity candidates, "
    "not confirmed duplicates."
)

print(
    "\nNo images were deleted or modified."
)

print("\n" + "=" * 75)
print("CHECK COMPLETED")
print("=" * 75)