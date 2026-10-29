from pathlib import Path
import hashlib
import json
import shutil

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASETS_DIR = PROJECT_ROOT / "datasets"
OUTPUT_DIR = PROJECT_ROOT / "data" / "unified"
RESULTS_DIR = PROJECT_ROOT / "results"

D1_DIR = DATASETS_DIR / "dataset_1_plantvillage"
D2_DIR = DATASETS_DIR / "dataset_2_crops_disease"
D6_DIR = DATASETS_DIR / "dataset_6_web_sourced"

DUPLICATE_FILE = RESULTS_DIR / "cross_dataset_duplicates.json"
SUMMARY_FILE = RESULTS_DIR / "unified_dataset_summary.json"


# ============================================================
# VALIDATED CLASS MAPPING
# ============================================================

CLASS_MAPPING = {
    "Potato_Early_Blight": {
        "dataset_1_plantvillage": "Potato___Early_blight",
        "dataset_2_crops_disease": "Potato___Early_Blight",
    },

    "Potato_Late_Blight": {
        "dataset_1_plantvillage": "Potato___Late_blight",
        "dataset_2_crops_disease": "Potato___Late_Blight",
    },

    "Potato_Healthy": {
        "dataset_1_plantvillage": "Potato___healthy",
        "dataset_2_crops_disease": "Potato___Healthy",
    },

    "Tomato_Bacterial_Spot": {
        "dataset_1_plantvillage": "Tomato_Bacterial_spot",
        "dataset_6_web_sourced": "tomato leaf bacterial spot",
    },

    "Tomato_Early_Blight": {
        "dataset_1_plantvillage": "Tomato_Early_blight",
        "dataset_6_web_sourced": "tomato leaf early blight",
    },

    "Tomato_Late_Blight": {
        "dataset_1_plantvillage": "Tomato_Late_blight",
        "dataset_6_web_sourced": "tomato leaf late blight",
    },

    "Tomato_Leaf_Mold": {
        "dataset_1_plantvillage": "Tomato_Leaf_Mold",
        "dataset_6_web_sourced": "tomato leaf mold",
    },

    "Tomato_Septoria_Leaf_Spot": {
        "dataset_1_plantvillage": "Tomato_Septoria_leaf_spot",
        "dataset_6_web_sourced": "tomato septoria leaf spot",
    },

    "Tomato_Healthy": {
        "dataset_1_plantvillage": "Tomato_healthy",
        "dataset_6_web_sourced": "tomato leaf healthy",
    },

    "Corn_Gray_Leaf_Spot": {
        "dataset_2_crops_disease": "Corn___Gray_Leaf_Spot",
        "dataset_6_web_sourced": "corn gray leaf spot",
    },

    "Corn_Leaf_Blight": {
        "dataset_6_web_sourced": "corn leaf blight",
    },

    "Corn_Leaf_Rust": {
        "dataset_6_web_sourced": "corn leaf rust",
    },

    "Apple_Healthy": {
        "dataset_6_web_sourced": "apple leaf healthy",
    },

    "Apple_Rust": {
        "dataset_6_web_sourced": "apple leaf rust",
    },

    "Apple_Scab": {
        "dataset_6_web_sourced": "apple leaf scab",
    },

    "Potato_Leaf_Blight": {
        "dataset_6_web_sourced": "potato leaf blight",
    },

    "Potato_Leafroll_Virus": {
        "dataset_6_web_sourced": "potato leafroll virus",
    },
}


# ============================================================
# IMAGE EXTENSIONS
# ============================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


# ============================================================
# FUNCTIONS
# ============================================================

def calculate_sha256(file_path):
    """Calculate SHA-256 hash of an image."""

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


def collect_images(dataset_dir):
    """Collect all image files recursively."""

    return [
        path
        for path in dataset_dir.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    ]


def load_duplicate_paths():
    """
    Load the 150 confirmed D1-D2 duplicate pairs.

    We exclude the Dataset 2 copy and retain the Dataset 1 copy.
    """

    if not DUPLICATE_FILE.exists():
        raise FileNotFoundError(
            f"Duplicate file not found:\n{DUPLICATE_FILE}"
        )

    with open(DUPLICATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    duplicate_d2_paths = set()

    for item in data["duplicates"]:
        duplicate_d2_paths.add(
            item["dataset_2"].replace("\\", "/")
        )

    return duplicate_d2_paths


def find_class_for_file(file_path, dataset_name):
    """
    Determine the original class folder for an image.

    The function checks parent folders against the validated mapping.
    """

    possible_classes = set()

    for unified_class, dataset_mapping in CLASS_MAPPING.items():

        if dataset_name in dataset_mapping:
            possible_classes.add(
                dataset_mapping[dataset_name]
            )

    for parent in file_path.parents:

        folder_name = parent.name

        if folder_name in possible_classes:
            return folder_name

    return None


def get_unified_class(dataset_name, original_class):
    """Convert original dataset class to unified class."""

    for unified_class, dataset_mapping in CLASS_MAPPING.items():

        if dataset_mapping.get(dataset_name) == original_class:
            return unified_class

    return None


def copy_image(source_path, unified_class, dataset_name, counter):
    """
    Copy image to unified dataset.

    Dataset prefix prevents filename collisions.
    """

    destination_class_dir = OUTPUT_DIR / unified_class
    destination_class_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    new_name = (
        f"{dataset_name}__"
        f"{counter:06d}__"
        f"{source_path.name}"
    )

    destination_path = destination_class_dir / new_name

    shutil.copy2(
        source_path,
        destination_path
    )

    return destination_path


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("CREATING CLEAN UNIFIED DATASET")
    print("=" * 70)

    # --------------------------------------------------------
    # Check required folders/files
    # --------------------------------------------------------

    for directory in [D1_DIR, D2_DIR, D6_DIR]:

        if not directory.exists():
            raise FileNotFoundError(
                f"Dataset folder not found:\n{directory}"
            )

    if not DUPLICATE_FILE.exists():
        raise FileNotFoundError(
            f"Duplicate list not found:\n{DUPLICATE_FILE}"
        )

    # --------------------------------------------------------
    # Remove previous unified dataset if it exists
    # --------------------------------------------------------

    if OUTPUT_DIR.exists():

        print("\nRemoving previous unified dataset...")

        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Load duplicate list
    # --------------------------------------------------------

    duplicate_d2_paths = load_duplicate_paths()

    print(
        f"\nConfirmed D1-D2 duplicates to exclude: "
        f"{len(duplicate_d2_paths)}"
    )

    # --------------------------------------------------------
    # Dataset configuration
    # --------------------------------------------------------

    datasets = [
        (
            "dataset_1_plantvillage",
            D1_DIR
        ),
        (
            "dataset_2_crops_disease",
            D2_DIR
        ),
        (
            "dataset_6_web_sourced",
            D6_DIR
        ),
    ]

    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    dataset_counts = {
        "dataset_1_plantvillage": 0,
        "dataset_2_crops_disease": 0,
        "dataset_6_web_sourced": 0,
    }

    class_counts = {
        unified_class: 0
        for unified_class in CLASS_MAPPING
    }

    skipped_unmapped = 0
    skipped_duplicates = 0

    processed_records = []

    # --------------------------------------------------------
    # Process datasets
    # --------------------------------------------------------

    for dataset_name, dataset_dir in datasets:

        print("\n" + "-" * 70)
        print(f"Processing: {dataset_name}")
        print("-" * 70)

        images = collect_images(dataset_dir)

        print(f"Images found: {len(images)}")

        counter = 0

        for image_path in images:

            # ------------------------------------------------
            # Check duplicate D2 path
            # ------------------------------------------------

            if dataset_name == "dataset_2_crops_disease":

                relative_path = image_path.relative_to(
                    dataset_dir
                )

                relative_path_string = str(
                    relative_path
                ).replace("\\", "/")

                if relative_path_string in duplicate_d2_paths:

                    skipped_duplicates += 1

                    continue

            # ------------------------------------------------
            # Find original class
            # ------------------------------------------------

            original_class = find_class_for_file(
                image_path,
                dataset_name
            )

            if original_class is None:

                skipped_unmapped += 1

                continue

            # ------------------------------------------------
            # Convert to unified class
            # ------------------------------------------------

            unified_class = get_unified_class(
                dataset_name,
                original_class
            )

            if unified_class is None:

                skipped_unmapped += 1

                continue

            # ------------------------------------------------
            # Copy image
            # ------------------------------------------------

            counter += 1

            destination = copy_image(
                image_path,
                unified_class,
                dataset_name,
                counter
            )

            dataset_counts[dataset_name] += 1
            class_counts[unified_class] += 1

            processed_records.append({
                "dataset": dataset_name,
                "original_class": original_class,
                "unified_class": unified_class,
                "source": str(
                    image_path.relative_to(dataset_dir)
                ).replace("\\", "/"),
                "destination": str(
                    destination.relative_to(OUTPUT_DIR)
                ).replace("\\", "/"),
            })

            if counter % 500 == 0:
                print(
                    f"Copied {counter} images..."
                )

        print(
            f"Included from {dataset_name}: "
            f"{dataset_counts[dataset_name]}"
        )

    # --------------------------------------------------------
    # Save summary
    # --------------------------------------------------------

    total_images = sum(
        class_counts.values()
    )

    summary = {
        "description": (
            "Clean unified classification dataset "
            "created from Datasets 1, 2 and 6"
        ),

        "datasets_used": [
            "dataset_1_plantvillage",
            "dataset_2_crops_disease",
            "dataset_6_web_sourced"
        ],

        "unified_class_count": len(
            CLASS_MAPPING
        ),

        "total_images": total_images,

        "dataset_counts": dataset_counts,

        "class_counts": class_counts,

        "confirmed_duplicates_excluded": skipped_duplicates,

        "unmapped_images_skipped": skipped_unmapped,

        "near_duplicate_candidate": {
            "status": "NOT_REMOVED",
            "reason": (
                "Only a near-duplicate candidate; "
                "not a confirmed duplicate."
            )
        },

        "raw_datasets_modified": False
    }

    with open(
        SUMMARY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            summary,
            f,
            indent=4
        )

    # --------------------------------------------------------
    # Save processing records
    # --------------------------------------------------------

    records_file = (
        RESULTS_DIR /
        "unified_dataset_records.json"
    )

    with open(
        records_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            processed_records,
            f,
            indent=2
        )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("UNIFIED DATASET CREATION COMPLETE")
    print("=" * 70)

    print(
        f"\nUnified classes: "
        f"{len(CLASS_MAPPING)}"
    )

    print(
        f"Total images: "
        f"{total_images}"
    )

    print(
        f"Confirmed duplicates excluded: "
        f"{skipped_duplicates}"
    )

    print(
        f"Unmapped images skipped: "
        f"{skipped_unmapped}"
    )

    print("\nDataset-wise counts:")

    for dataset, count in dataset_counts.items():

        print(
            f"  {dataset}: {count}"
        )

    print("\nClass-wise counts:")

    for class_name, count in class_counts.items():

        print(
            f"  {class_name}: {count}"
        )

    print("\nOutput directory:")
    print(OUTPUT_DIR)

    print("\nSummary file:")
    print(SUMMARY_FILE)

    print("\nRaw datasets were NOT modified.")


if __name__ == "__main__":
    main()