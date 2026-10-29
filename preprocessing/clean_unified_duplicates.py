from pathlib import Path
import json
import shutil

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

UNIFIED_DIR = PROJECT_ROOT / "data" / "unified"
CLEAN_DIR = PROJECT_ROOT / "data" / "unified_clean"

ANALYSIS_FILE = (
    PROJECT_ROOT
    / "results"
    / "unified_duplicate_analysis.json"
)

REPORT_FILE = (
    PROJECT_ROOT
    / "results"
    / "unified_duplicate_cleanup_report.json"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("CLEANING UNIFIED DATASET DUPLICATES")
    print("=" * 70)

    if not UNIFIED_DIR.exists():
        raise FileNotFoundError(
            f"Unified dataset not found:\n{UNIFIED_DIR}"
        )

    if not ANALYSIS_FILE.exists():
        raise FileNotFoundError(
            f"Duplicate analysis not found:\n{ANALYSIS_FILE}"
        )

    # --------------------------------------------------------
    # Load duplicate analysis
    # --------------------------------------------------------

    with open(
        ANALYSIS_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        analysis = json.load(f)

    same_class_groups = analysis[
        "same_class_groups"
    ]

    cross_class_groups = analysis[
        "cross_class_groups"
    ]

    print(
        f"\nSame-class duplicate groups: "
        f"{len(same_class_groups)}"
    )

    print(
        f"Cross-class duplicate groups: "
        f"{len(cross_class_groups)}"
    )

    # --------------------------------------------------------
    # Create set of files to remove
    # --------------------------------------------------------

    files_to_remove = set()

    # --------------------------------------------------------
    # Cross-class duplicates
    #
    # Remove ALL files in these groups because the same
    # image has conflicting labels.
    # --------------------------------------------------------

    for group in cross_class_groups:

        for file_path in group["files"]:

            files_to_remove.add(
                file_path.replace("\\", "/")
            )

    # --------------------------------------------------------
    # Same-class duplicates
    #
    # Keep the first image and remove the remaining copies.
    # --------------------------------------------------------

    same_class_removed = 0

    for group in same_class_groups:

        files = [
            path.replace("\\", "/")
            for path in group["files"]
        ]

        # Keep first
        for duplicate_file in files[1:]:

            files_to_remove.add(
                duplicate_file
            )

            same_class_removed += 1

    # --------------------------------------------------------
    # Recreate clean directory
    # --------------------------------------------------------

    if CLEAN_DIR.exists():

        print("\nRemoving previous cleaned dataset...")

        shutil.rmtree(CLEAN_DIR)

    CLEAN_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Copy all images except those marked for removal
    # --------------------------------------------------------

    all_images = [
        path
        for path in UNIFIED_DIR.rglob("*")
        if path.is_file()
    ]

    copied_count = 0
    removed_count = 0

    for image_path in all_images:

        relative_path = str(
            image_path.relative_to(UNIFIED_DIR)
        ).replace("\\", "/")

        destination = CLEAN_DIR / relative_path

        if relative_path in files_to_remove:

            removed_count += 1
            continue

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copy2(
            image_path,
            destination
        )

        copied_count += 1

        if copied_count % 1000 == 0:

            print(
                f"Copied {copied_count} images..."
            )

    # --------------------------------------------------------
    # Count cleaned classes
    # --------------------------------------------------------

    class_counts = {}

    for class_dir in CLEAN_DIR.iterdir():

        if not class_dir.is_dir():
            continue

        count = sum(
            1
            for file in class_dir.rglob("*")
            if file.is_file()
        )

        class_counts[class_dir.name] = count

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    report = {

        "original_dataset": str(
            UNIFIED_DIR
        ),

        "cleaned_dataset": str(
            CLEAN_DIR
        ),

        "original_image_count": len(
            all_images
        ),

        "cleaned_image_count": copied_count,

        "removed_image_count": removed_count,

        "cross_class_duplicate_groups_removed": len(
            cross_class_groups
        ),

        "same_class_duplicate_groups_found": len(
            same_class_groups
        ),

        "same_class_duplicate_copies_removed": same_class_removed,

        "class_counts": class_counts,

        "raw_datasets_modified": False
    }

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            report,
            f,
            indent=4
        )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)

    print(
        f"\nOriginal images: "
        f"{len(all_images)}"
    )

    print(
        f"Removed images: "
        f"{removed_count}"
    )

    print(
        f"Cleaned images: "
        f"{copied_count}"
    )

    print("\nClass-wise counts:")

    for class_name in sorted(class_counts):

        print(
            f"  {class_name}: "
            f"{class_counts[class_name]}"
        )

    print("\nClean dataset:")
    print(CLEAN_DIR)

    print("\nCleanup report:")
    print(REPORT_FILE)

    print("\nRaw datasets were NOT modified.")


if __name__ == "__main__":
    main()