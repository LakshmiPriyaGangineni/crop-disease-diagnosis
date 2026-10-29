from pathlib import Path
import json

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = PROJECT_DIR / "datasets"

# --------------------------------------------------
# Standardized class mapping
# --------------------------------------------------

CLASS_MAPPING = {

    # Potato
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

    # Tomato
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

    # Corn
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

    # Apple
    "Apple_Healthy": {
        "dataset_6_web_sourced": "apple leaf healthy",
    },

    "Apple_Rust": {
        "dataset_6_web_sourced": "apple leaf rust",
    },

    "Apple_Scab": {
        "dataset_6_web_sourced": "apple leaf scab",
    },

    # Potato additional classes from Dataset 6
    "Potato_Leaf_Blight": {
        "dataset_6_web_sourced": "potato leaf blight",
    },

    "Potato_Leafroll_Virus": {
        "dataset_6_web_sourced": "potato leafroll virus",
    },
}


# --------------------------------------------------
# Print mapping
# --------------------------------------------------

print("=" * 75)
print("STANDARDIZED CLASS MAPPING")
print("=" * 75)

for standard_class, datasets in CLASS_MAPPING.items():

    print(f"\n{standard_class}")
    print("-" * 50)

    for dataset, original_class in datasets.items():
        print(f"  {dataset}")
        print(f"    → {original_class}")


# --------------------------------------------------
# Save mapping as JSON
# --------------------------------------------------

output_file = PROJECT_DIR / "results" / "class_mapping.json"

output_file.parent.mkdir(exist_ok=True)

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(
        CLASS_MAPPING,
        file,
        indent=4
    )

print("\n" + "=" * 75)
print("Mapping saved successfully.")
print(f"File: {output_file}")
print("=" * 75)