import os

DATA_DIR = "data"
splits = ["train", "validation", "test"]

grand_total = 0

for split in splits:
    split_path = os.path.join(DATA_DIR, split)
    split_total = 0

    print(f"\n{split.upper()}")

    for class_name in sorted(os.listdir(split_path)):
        class_path = os.path.join(split_path, class_name)

        if not os.path.isdir(class_path):
            continue

        count = sum(
            1 for file in os.listdir(class_path)
            if file.lower().endswith((".jpg", ".jpeg", ".png"))
        )

        print(f"{class_name}: {count}")
        split_total += count

    print(f"Total {split}: {split_total}")
    grand_total += split_total

print(f"\nGrand Total: {grand_total}")

if grand_total == 20638:
    print("SUCCESS: All 20,638 images are present.")
else:
    print("WARNING: Image count does not match 20,638.")