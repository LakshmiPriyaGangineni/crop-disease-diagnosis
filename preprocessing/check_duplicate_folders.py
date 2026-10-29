import os
import hashlib

OUTER = "PlantVillage"
INNER = os.path.join("PlantVillage", "PlantVillage")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def get_image_files(folder):
    files = {}

    if not os.path.exists(folder):
        return files

    for file_name in os.listdir(folder):
        file_path = os.path.join(folder, file_name)

        if not os.path.isfile(file_path):
            continue

        extension = os.path.splitext(file_name)[1].lower()

        if extension in IMAGE_EXTENSIONS:
            files[file_name] = file_path

    return files


def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            data = file.read(1024 * 1024)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


print("=" * 70)
print("COMPARING OUTER AND INNER PLANTVILLAGE DATASETS")
print("=" * 70)

classes = [
    folder
    for folder in os.listdir(OUTER)
    if os.path.isdir(os.path.join(OUTER, folder))
    and folder != "PlantVillage"
]

all_identical = True

for class_name in sorted(classes):

    outer_path = os.path.join(OUTER, class_name)
    inner_path = os.path.join(INNER, class_name)

    outer_files = get_image_files(outer_path)
    inner_files = get_image_files(inner_path)

    print(f"\nChecking: {class_name}")

    if set(outer_files.keys()) != set(inner_files.keys()):
        print("  ❌ File names are different.")
        all_identical = False
        continue

    class_identical = True

    for file_name in outer_files:

        outer_hash = calculate_hash(outer_files[file_name])
        inner_hash = calculate_hash(inner_files[file_name])

        if outer_hash != inner_hash:
            print(f"  ❌ Different image: {file_name}")
            class_identical = False
            all_identical = False

    if class_identical:
        print(f"  ✅ All {len(outer_files)} images are identical.")

print("\n" + "=" * 70)

if all_identical:
    print("✅ RESULT: BOTH DATASETS ARE IDENTICAL.")
    print("The inner PlantVillage folder is a duplicate.")
    print("You can safely delete the INNER PlantVillage folder.")
else:
    print("❌ RESULT: DIFFERENCES FOUND.")
    print("DO NOT delete the inner PlantVillage folder yet.")

print("=" * 70)