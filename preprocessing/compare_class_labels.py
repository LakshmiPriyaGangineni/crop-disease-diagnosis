from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = PROJECT_DIR / "datasets"


def get_class_folders(dataset_path):
    """
    Find folders that directly contain images.
    """
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    classes = set()

    for folder in dataset_path.rglob("*"):
        if folder.is_dir():
            has_images = any(
                file.is_file()
                and file.suffix.lower() in image_extensions
                for file in folder.iterdir()
            )

            if has_images:
                # Use the folder name as the class label
                classes.add(folder.name)

    return classes


datasets = {
    "Dataset 1 - PlantVillage": "dataset_1_plantvillage",
    "Dataset 2 - Crops Disease": "dataset_2_crops_disease",
    "Dataset 3 - Plant Disease": "dataset_3_plant_disease",
    "Dataset 6 - Web Sourced": "dataset_6_web_sourced",
}


all_classes = {}

print("=" * 75)
print("CLASS LABEL COMPARISON")
print("=" * 75)

# --------------------------------------------------
# Collect classes
# --------------------------------------------------

for dataset_name, folder_name in datasets.items():

    dataset_path = DATASETS_DIR / folder_name

    classes = get_class_folders(dataset_path)

    all_classes[dataset_name] = classes

    print(f"\n{dataset_name}")
    print("-" * 75)

    for class_name in sorted(classes):
        print(class_name)

    print(f"\nNumber of classes: {len(classes)}")


# --------------------------------------------------
# Find exact common labels
# --------------------------------------------------

print("\n" + "=" * 75)
print("EXACT COMMON CLASS LABELS")
print("=" * 75)

dataset_names = list(all_classes.keys())

for i in range(len(dataset_names)):
    for j in range(i + 1, len(dataset_names)):

        name1 = dataset_names[i]
        name2 = dataset_names[j]

        common = all_classes[name1] & all_classes[name2]

        print(f"\n{name1} ↔ {name2}")
        print(f"Common labels: {len(common)}")

        if common:
            for label in sorted(common):
                print(f"  {label}")
        else:
            print("  None")


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\n" + "=" * 75)
print("CLASS COMPARISON COMPLETED")
print("=" * 75)