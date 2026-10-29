from pathlib import Path
from collections import Counter


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = PROJECT_DIR / "datasets"


def analyze_files(folder):
    print(f"\nScanning: {folder}")

    if not folder.exists():
        print("Folder not found.")
        return

    files = [f for f in folder.rglob("*") if f.is_file()]

    print(f"Total files: {len(files)}")

    extensions = Counter(
        f.suffix.lower() if f.suffix else "[no extension]"
        for f in files
    )

    print("\nFile types:")
    for ext, count in sorted(extensions.items()):
        print(f"  {ext}: {count}")

    print("\nSample files:")

    for file in files[:20]:
        print(f"  {file.relative_to(folder)}")


# ==================================================
# DATASET 4
# ==================================================

dataset4 = DATASETS_DIR / "dataset_4_multi_crop_disease"

print("=" * 70)
print("DATASET 4 - ANNOTATION ANALYSIS")
print("=" * 70)

analyze_files(dataset4)

print("\n\nFolders inside Dataset 4:")

for folder in sorted(dataset4.rglob("*")):
    if folder.is_dir():
        print(f"  {folder.relative_to(dataset4)}")


# ==================================================
# DATASET 5
# ==================================================

dataset5 = DATASETS_DIR / "dataset_5_plantseg"

print("\n" + "=" * 70)
print("DATASET 5 - ANNOTATION ANALYSIS")
print("=" * 70)

analyze_files(dataset5)

print("\n\nFolders inside Dataset 5:")

for folder in sorted(dataset5.rglob("*")):
    if folder.is_dir():
        print(f"  {folder.relative_to(dataset5)}")


print("\n" + "=" * 70)
print("ANALYSIS COMPLETED")
print("=" * 70)