from pathlib import Path
import json
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent

VERIFICATION_FILE = (
    PROJECT_ROOT
    / "results"
    / "unified_dataset_verification.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "unified_duplicate_analysis.json"
)


def get_class(file_path):
    """
    The unified dataset structure is:

    data/unified/
        Class_Name/
            image.jpg
    """

    parts = Path(file_path).parts

    if len(parts) >= 2:
        return parts[0]

    return "UNKNOWN"


def get_dataset(file_path):
    """
    Filenames created by create_unified_dataset.py use:

    dataset_name__000001__original_filename.jpg
    """

    filename = Path(file_path).name

    if "__" in filename:
        return filename.split("__")[0]

    return "UNKNOWN"


def main():

    print("=" * 70)
    print("ANALYZING UNIFIED DATASET DUPLICATES")
    print("=" * 70)

    if not VERIFICATION_FILE.exists():
        raise FileNotFoundError(
            f"Verification file not found:\n{VERIFICATION_FILE}"
        )

    with open(
        VERIFICATION_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        verification = json.load(f)

    duplicate_groups = verification.get(
        "duplicate_groups_details",
        []
    )

    print(
        f"\nDuplicate groups found: "
        f"{len(duplicate_groups)}"
    )

    same_class_groups = []
    cross_class_groups = []
    same_dataset_groups = []
    cross_dataset_groups = []

    for index, group in enumerate(
        duplicate_groups,
        start=1
    ):

        classes = set()
        datasets = set()

        for file_path in group:

            classes.add(
                get_class(file_path)
            )

            datasets.add(
                get_dataset(file_path)
            )

        if len(classes) == 1:
            same_class_groups.append({
                "group": index,
                "files": group,
                "classes": sorted(classes),
                "datasets": sorted(datasets)
            })

        else:
            cross_class_groups.append({
                "group": index,
                "files": group,
                "classes": sorted(classes),
                "datasets": sorted(datasets)
            })

        if len(datasets) == 1:
            same_dataset_groups.append({
                "group": index,
                "files": group,
                "classes": sorted(classes),
                "datasets": sorted(datasets)
            })

        else:
            cross_dataset_groups.append({
                "group": index,
                "files": group,
                "classes": sorted(classes),
                "datasets": sorted(datasets)
            })

    # ========================================================
    # DISPLAY
    # ========================================================

    print("\n" + "-" * 70)
    print("SUMMARY")
    print("-" * 70)

    print(
        f"Same-class duplicate groups: "
        f"{len(same_class_groups)}"
    )

    print(
        f"Cross-class duplicate groups: "
        f"{len(cross_class_groups)}"
    )

    print(
        f"Same-dataset duplicate groups: "
        f"{len(same_dataset_groups)}"
    )

    print(
        f"Cross-dataset duplicate groups: "
        f"{len(cross_dataset_groups)}"
    )

    # ========================================================
    # SAME-CLASS DUPLICATES
    # ========================================================

    print("\n" + "-" * 70)
    print("SAME-CLASS DUPLICATES")
    print("-" * 70)

    for item in same_class_groups:

        print(
            f"\nGroup {item['group']}"
        )

        print(
            f"Class: {item['classes'][0]}"
        )

        print(
            f"Datasets: {', '.join(item['datasets'])}"
        )

        for file_path in item["files"]:
            print(
                f"  {file_path}"
            )

    # ========================================================
    # CROSS-CLASS DUPLICATES
    # ========================================================

    print("\n" + "-" * 70)
    print("CROSS-CLASS DUPLICATES")
    print("-" * 70)

    if not cross_class_groups:

        print(
            "None found. This is good."
        )

    else:

        for item in cross_class_groups:

            print(
                f"\nGroup {item['group']}"
            )

            print(
                f"Classes: "
                f"{', '.join(item['classes'])}"
            )

            print(
                f"Datasets: "
                f"{', '.join(item['datasets'])}"
            )

            for file_path in item["files"]:
                print(
                    f"  {file_path}"
                )

    # ========================================================
    # CROSS-DATASET DUPLICATES
    # ========================================================

    print("\n" + "-" * 70)
    print("CROSS-DATASET DUPLICATES")
    print("-" * 70)

    for item in cross_dataset_groups:

        print(
            f"\nGroup {item['group']}"
        )

        print(
            f"Class: "
            f"{', '.join(item['classes'])}"
        )

        print(
            f"Datasets: "
            f"{', '.join(item['datasets'])}"
        )

        for file_path in item["files"]:
            print(
                f"  {file_path}"
            )

    # ========================================================
    # SAVE REPORT
    # ========================================================

    analysis = {
        "total_duplicate_groups": len(
            duplicate_groups
        ),

        "same_class_duplicate_groups": len(
            same_class_groups
        ),

        "cross_class_duplicate_groups": len(
            cross_class_groups
        ),

        "same_dataset_duplicate_groups": len(
            same_dataset_groups
        ),

        "cross_dataset_duplicate_groups": len(
            cross_dataset_groups
        ),

        "same_class_groups": same_class_groups,

        "cross_class_groups": cross_class_groups,

        "same_dataset_groups": same_dataset_groups,

        "cross_dataset_groups": cross_dataset_groups
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            analysis,
            f,
            indent=4
        )

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    print(
        f"\nReport saved to:\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()