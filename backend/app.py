# =========================================
# CropCure AI - Flask Backend
# =========================================

import json
import os
import sys
import urllib.parse

# =========================================
# Add Project Root to Python Path
# =========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from inference.cnn_inference import (
    predict_image,
    load_model,
    InvalidImageError,
    ModelLoadError,
)
from rag.llm_service import answer_query, answer_query_with_cnn
from rag.retriever import get_disease_entry

# Approved Evaluation Paths (Strictly inside project directory)
EVALUATION_DIR = os.path.join(BASE_DIR, "results", "cnn_evaluation")
UNIFIED_SUMMARY_PATH = os.path.join(BASE_DIR, "results", "unified_dataset_summary.json")
GOVERNMENT_SCHEMES_PATH = os.path.join(BASE_DIR, "rag", "government_schemes.json")

# =========================================
# Flask Application
# =========================================

app = Flask(__name__)
CORS(app)



# =========================================
# Pre-warm / Verify CNN Model
# =========================================

def init_model():
    try:
        load_model()
        print("CNN model initialized and verified successfully.")
    except Exception as exc:
        print(f"Warning: Could not pre-load CNN model: {exc}")


# =========================================
# Home Route
# =========================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "success",
        "message": "CropCure AI backend is running",
        "service": "Crop Disease Diagnosis API"
    })


# =========================================
# CNN Prediction Route
# =========================================

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({
            "status": "error",
            "message": "No image uploaded"
        }), 400

    image_file = request.files["image"]

    if not image_file or image_file.filename == "":
        return jsonify({
            "status": "error",
            "message": "No image selected"
        }), 400

    try:
        # Run CNN prediction via inference.cnn_inference.predict_image
        result = predict_image(image_file.stream)

        # Look up authoritative knowledge base entry if available
        entry = get_disease_entry(result["predicted_class"])
        knowledge = None
        if entry:
            knowledge = {
                "crop": entry.get("crop", ""),
                "disease": entry.get("disease", ""),
                "symptoms": entry.get("symptoms", []),
                "treatment": entry.get("treatment", ""),
                "prevention": entry.get("prevention", ""),
            }

        return jsonify({
            "status": "success",
            "prediction": result["predicted_class"],
            "predicted_class": result["predicted_class"],
            "confidence": result["confidence"],
            "class_index": result["class_index"],
            "top3": result["top3"],
            "uncertain": result.get("uncertain", result["confidence"] < 0.50),
            "warning": result.get("warning"),
            "knowledge": knowledge
        }), 200

    except InvalidImageError as error:
        return jsonify({
            "status": "error",
            "message": f"Invalid image: {error}",
            "error": str(error)
        }), 400

    except ModelLoadError as error:
        return jsonify({
            "status": "error",
            "message": f"CNN model error: {error}",
            "error": str(error)
        }), 503

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": "Failed to process image.",
            "error": str(error)
        }), 500


# =========================================
# Chat Route (RAG + Groq LLM + CNN Visual Grounding)
# =========================================

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "status": "error",
            "message": "No chat message provided"
        }), 400

    # Support either "message" or "question"
    message = data.get("message")
    if not message and "question" in data:
        message = data.get("question")

    if not message or not isinstance(message, str) or not message.strip():
        return jsonify({
            "success": False,
            "status": "error",
            "message": "Chat message cannot be empty"
        }), 400

    # Optional CNN visual diagnosis fields
    predicted_disease = (
        data.get("predicted_disease")
        or data.get("predicted_class")
        or data.get("prediction")
    )
    confidence = data.get("confidence")
    top3 = data.get("top3")

    # Language selection (default: "en", supports "te" for Telugu, "hi" for Hindi)
    raw_lang = data.get("language", "en")
    language = str(raw_lang).strip().lower() if raw_lang else "en"
    if language not in ("en", "te", "hi"):
        language = "en"

    # If visual diagnosis info is provided, run grounded CNN + RAG + LLM flow
    if predicted_disease is not None or confidence is not None:
        result = answer_query_with_cnn(
            user_query=message,
            predicted_disease=predicted_disease,
            confidence=confidence,
            top3=top3,
            top_k=3,
            language=language
        )
    else:
        # Standard RAG retrieval + grounded LLM answer
        result = answer_query(message, top_k=3, language=language)

    if result["success"]:
        response_payload = {
            "success": True,
            "status": "success",
            "answer": result["answer"],
            "sources": result["sources"],
        }
        if "uncertain" in result:
            response_payload["uncertain"] = result["uncertain"]
        if "warning" in result:
            response_payload["warning"] = result["warning"]
        if "candidates" in result and result["candidates"] is not None:
            response_payload["candidates"] = result["candidates"]
        if "knowledge" in result and result["knowledge"] is not None:
            response_payload["knowledge"] = result["knowledge"]
        return jsonify(response_payload), 200

    error_code = result.get("error")
    http_status = 503 if error_code in (
        "missing_api_key", "llm_error"
    ) else 200 if error_code == "no_documents" else 400

    return jsonify({
        "success": False,
        "status": "error",
        "message": result["answer"],
        "answer": result["answer"],
        "sources": result.get("sources", [])
    }), http_status


# =========================================
# Model Evaluation Routes (Step 3)
# =========================================

def load_evaluation_data(eval_dir=EVALUATION_DIR, summary_path=UNIFIED_SUMMARY_PATH):
    """
    Read approved offline evaluation results from saved project artifacts.
    Guarantees no arbitrary filesystem access and handles missing/malformed files.
    Returns: (data_dict, error_dict, http_status_code)
    """
    test_metrics_file = os.path.join(eval_dir, "test_metrics.json")
    per_class_file = os.path.join(eval_dir, "per_class_metrics.json")
    cm_file = os.path.join(eval_dir, "confusion_matrix.json")

    missing = []
    for fpath, fname in [
        (test_metrics_file, "test_metrics.json"),
        (per_class_file, "per_class_metrics.json"),
        (cm_file, "confusion_matrix.json")
    ]:
        if not os.path.isfile(fpath):
            missing.append(fname)

    if missing:
        return None, {
            "status": "error",
            "message": f"Evaluation artifacts not found: {', '.join(missing)}"
        }, 404

    try:
        with open(test_metrics_file, "r", encoding="utf-8") as f:
            test_metrics = json.load(f)
        with open(per_class_file, "r", encoding="utf-8") as f:
            per_class = json.load(f)
        with open(cm_file, "r", encoding="utf-8") as f:
            cm = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, {
            "status": "error",
            "message": f"Malformed evaluation artifact JSON: {str(exc)}"
        }, 500

    # Dataset split info from unified_dataset_summary.json (if present)
    summary_data = None
    if os.path.isfile(summary_path):
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                summary_data = json.load(f)
        except Exception:
            summary_data = None

    split_details = {
        "train_ratio": "70%",
        "val_ratio": "15%",
        "test_ratio": "15%",
        "split_description": "70% Train / 15% Validation / 15% Test (stratified by class, random seed 42)",
        "total_test_images": test_metrics.get("total_test_images", 1903),
        "total_dataset_images": summary_data.get("total_images", 12702) if summary_data else 12702,
        "num_classes": test_metrics.get("num_classes", 17),
        "evaluation_split": "data/unified_test",
        "datasets_used": summary_data.get("datasets_used", [
            "dataset_1_plantvillage", "dataset_2_crops_disease", "dataset_6_web_sourced"
        ]) if summary_data else ["dataset_1_plantvillage", "dataset_2_crops_disease", "dataset_6_web_sourced"]
    }

    result = {
        "status": "success",
        "model_name": "CropDiseaseCNN",
        "evaluation_scope": "Offline test-set evaluation (data/unified_test)",
        "disclaimer": (
            "These metrics reflect offline performance evaluated on the held-out unified test dataset (1,903 images across 17 classes). "
            "Offline test metrics demonstrate strong generalized pattern recognition across supported classes, "
            "but do not guarantee that an individual real-world prediction is correct, especially under varied field lighting, "
            "symptom overlap, or unsupported sample conditions."
        ),
        "summary": {
            "overall_test_accuracy": test_metrics.get("overall_test_accuracy"),
            "overall_test_accuracy_pct": test_metrics.get("overall_test_accuracy_pct"),
            "top3_accuracy": test_metrics.get("top3_accuracy"),
            "top3_accuracy_pct": test_metrics.get("top3_accuracy_pct"),
            "total_test_images": test_metrics.get("total_test_images"),
            "total_correct": test_metrics.get("total_correct"),
            "total_incorrect": test_metrics.get("total_incorrect"),
            "num_classes": test_metrics.get("num_classes"),
        },
        "macro_metrics": test_metrics.get("macro_avg", {}),
        "weighted_metrics": test_metrics.get("weighted_avg", {}),
        "split_details": split_details,
        "per_class_metrics": per_class,
        "confusion_matrix": cm,
    }
    return result, None, 200


@app.route("/evaluation", methods=["GET"])
def get_evaluation():
    """
    Read-only endpoint returning approved CNN test evaluation metrics
    from saved project artifacts. Strictly reads from constant paths within results/.
    """
    data, err, status = load_evaluation_data()
    if err:
        return jsonify(err), status
    return jsonify(data), 200


@app.route("/evaluation/confusion-matrix-image", methods=["GET"])
def get_confusion_matrix_image():
    """Serve the static confusion matrix plot if available."""
    cm_img = os.path.join(EVALUATION_DIR, "confusion_matrix.png")
    if not os.path.isfile(cm_img):
        return jsonify({
            "status": "error",
            "message": "Confusion matrix image not found"
        }), 404
    return send_file(cm_img, mimetype="image/png")


# =========================================
# Government Agricultural Schemes (Step 4)
# =========================================

def load_government_schemes_data():
    """
    Safely load curated verified government agricultural schemes.
    Reads strictly from constant path within rag/.
    """
    if not os.path.isfile(GOVERNMENT_SCHEMES_PATH):
        return None, {
            "status": "error",
            "message": "Government schemes data file not found"
        }, 404

    try:
        with open(GOVERNMENT_SCHEMES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        return None, {
            "status": "error",
            "message": f"Malformed government schemes JSON: {exc}"
        }, 500

    return data, None, 200


@app.route("/schemes", methods=["GET"])
def get_schemes():
    """
    Return curated, verified Indian government agricultural schemes,
    with optional category filtering and keyword search.
    """
    data, err, status = load_government_schemes_data()
    if err:
        return jsonify(err), status

    schemes = data.get("schemes", [])
    category = request.args.get("category", "").strip().lower()
    query = request.args.get("q", "").strip().lower()

    if category and category != "all":
        schemes = [s for s in schemes if s.get("category", "").lower() == category]

    if query:
        filtered = []
        for s in schemes:
            name = s.get("name", "").lower()
            hindi_name = s.get("hindi_name", "").lower()
            purpose = s.get("purpose", "").lower()
            benefits = s.get("benefits", "").lower()
            eligibility = s.get("eligibility", "").lower()
            tags = [t.lower() for t in s.get("tags", [])]
            if (
                query in name
                or query in hindi_name
                or query in purpose
                or query in benefits
                or query in eligibility
                or any(query in t for t in tags)
            ):
                filtered.append(s)
        schemes = filtered

    return jsonify({
        "status": "success",
        "metadata": data.get("metadata", {}),
        "categories": data.get("categories", []),
        "schemes": schemes,
        "count": len(schemes)
    }), 200


@app.route("/schemes/categories", methods=["GET"])
def get_scheme_categories():
    """Return available scheme categories."""
    data, err, status = load_government_schemes_data()
    if err:
        return jsonify(err), status
    return jsonify({
        "status": "success",
        "categories": data.get("categories", [])
    }), 200


# =========================================
# Nearby Agricultural Input Shops (Step 5)
# =========================================

SHOP_CATEGORIES = [
    {
        "id": "all",
        "name": "General Agricultural Input Shops",
        "hindi_name": "कृषि सेवा केंद्र / सामान्य कृषि स्टोर",
        "description": "All-in-one agricultural stores, Krishi Seva Kendras, and PACS distributing seeds, fertilizers, and supplies",
        "icon": "🏪",
        "query_keyword": "krishi seva kendra agricultural input store",
    },
    {
        "id": "seeds",
        "name": "Seeds & Planting Material",
        "hindi_name": "बीज विक्रेता (Seeds)",
        "description": "Certified crop seeds, hybrid varieties, vegetable seedlings, and NSC certified outlets",
        "icon": "🌱",
        "query_keyword": "agricultural seeds store certified seeds shop",
    },
    {
        "id": "fertilizers",
        "name": "Fertilizers & Soil Nutrients",
        "hindi_name": "खाद एवं उर्वरक विक्रेता (Fertilizers)",
        "description": "Urea, DAP, NPK mixtures, bio-fertilizers, micronutrients, and IFFCO / KRIBHCO dealers",
        "icon": "🧪",
        "query_keyword": "fertilizers shop khad bhandar IFFCO center",
    },
    {
        "id": "pesticides",
        "name": "Pesticides & Crop Protection",
        "hindi_name": "कीटनाशक एवं फसल सुरक्षा (Pesticides)",
        "description": "Government-registered crop protection dealers, insecticides, fungicides, bio-pesticides, and spray chemicals",
        "icon": "🛡️",
        "query_keyword": "pesticides shop crop protection chemicals store",
    },
    {
        "id": "equipment",
        "name": "Agricultural Equipment & Tools",
        "hindi_name": "कृषि यंत्र एवं उपकरण (Equipment & Tools)",
        "description": "Knapsack sprayers, drip fittings, pump sets, spades, pruning tools, and farm implement spares",
        "icon": "🚜",
        "query_keyword": "agricultural equipment store farm tools sprayers",
    },
]


@app.route("/shops/categories", methods=["GET"])
def get_shop_categories():
    """Return supported agricultural input supply categories."""
    return jsonify({
        "status": "success",
        "categories": SHOP_CATEGORIES
    }), 200


@app.route("/shops/search", methods=["GET"])
def search_nearby_shops():
    """
    Generate verified external map service queries and links for nearby agricultural shops.
    Does NOT require a paid API key; links directly to Google Maps and OpenStreetMap.
    Guarantees no fabricated shop information.
    """
    raw_location = request.args.get("location", "").strip()
    if not raw_location:
        return jsonify({
            "status": "error",
            "message": "Please enter a valid location (city, town, village, or 6-digit PIN code)."
        }), 400

    # Sanitize location string: max 100 chars, remove control characters
    sanitized_location = "".join(c for c in raw_location if c.isalnum() or c in " ,.-_/")[:100].strip()
    if not sanitized_location:
        return jsonify({
            "status": "error",
            "message": "Invalid location format. Please enter a valid city, town, or PIN code."
        }), 400

    category_id = request.args.get("category", "all").strip().lower()
    selected_cat = next((c for c in SHOP_CATEGORIES if c["id"] == category_id), None)
    if not selected_cat:
        selected_cat = SHOP_CATEGORIES[0]

    # Construct search query for external maps
    query_text = f"{selected_cat['query_keyword']} near {sanitized_location}"
    encoded_query = urllib.parse.quote(query_text)

    # Google Maps Universal URL format (Free, official, cross-platform)
    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"
    # OpenStreetMap URL format (Free open source alternative)
    osm_url = f"https://www.openstreetmap.org/search?query={encoded_query}"
    # Directions URL
    directions_url = f"https://www.google.com/maps/dir/?api=1&destination={encoded_query}"

    # Build category-specific links for all 5 categories
    category_links = []
    for cat in SHOP_CATEGORIES:
        cat_q = f"{cat['query_keyword']} near {sanitized_location}"
        cat_encoded = urllib.parse.quote(cat_q)
        category_links.append({
            "category_id": cat["id"],
            "name": cat["name"],
            "hindi_name": cat["hindi_name"],
            "icon": cat["icon"],
            "description": cat["description"],
            "query_text": cat_q,
            "google_maps_url": f"https://www.google.com/maps/search/?api=1&query={cat_encoded}",
            "osm_url": f"https://www.openstreetmap.org/search?query={cat_encoded}",
        })

    return jsonify({
        "status": "success",
        "location": sanitized_location,
        "selected_category": selected_cat,
        "search_query": query_text,
        "primary_links": {
            "google_maps": google_maps_url,
            "openstreetmap": osm_url,
            "directions": directions_url,
        },
        "all_category_links": category_links,
        "disclaimer": (
            "Shop locations, opening hours, contact details, and directions are provided "
            "directly by external mapping services (Google Maps / OpenStreetMap). "
            "CropCure AI does not fabricate private shop stock, ratings, or pricing. "
            "Always verify chemical product registration and consult an agricultural extension officer."
        ),
        "source": "External Maps Service (Google Maps & OpenStreetMap)"
    }), 200


# =========================================
# Agriculture Expert Support (Step 7)
# =========================================

EXPERT_INSTITUTIONS = {
    "kisan_call_centre": {
        "name": "Kisan Call Centre (KCC)",
        "toll_free_number": "1800-180-1551",
        "operator": "Department of Agriculture & Farmers Welfare, Ministry of Agriculture & Farmers Welfare, Government of India",
        "operating_hours": "6:00 AM to 10:00 PM (All 7 Days a week)",
        "ivrs_availability": "24 hours a day, 365 days a year",
        "languages_supported": 22,
        "official_portal": "https://farmer.gov.in",
        "advisory": (
            "Farmers should confirm current service availability, timings, and local language options "
            "through official Government of India portals."
        ),
    },
    "krishi_vigyan_kendras": {
        "name": "Krishi Vigyan Kendras (KVK Network)",
        "network_size": "730+ KVKs covering rural districts of India",
        "apex_organization": "Indian Council of Agricultural Research (ICAR)",
        "official_portal": "https://kvk.icar.gov.in",
        "core_services": [
            "Front-line technology demonstration and field testing",
            "On-farm physical crop disease diagnosis and pest surveillance",
            "Soil and irrigation water testing laboratories",
            "Scientific advisory for local agro-climatic conditions",
        ],
    },
    "state_departments": {
        "name": "State Agriculture Departments & Krishi Bhavans",
        "hierarchy": "District Agriculture Offices (DAO) and Block-level Agriculture Development Offices (ADO)",
        "official_portal": "https://agricoop.nic.in",
        "core_services": [
            "Official field inspection by Agricultural Extension Officers",
            "Pest outbreak surveillance and management advisories",
            "Certification of approved inputs and subsidized bio-controls",
        ],
    },
    "agricultural_universities": {
        "name": "State Agricultural Universities (SAUs) & ICAR Institutes",
        "official_portal": "https://icar.org.in",
        "core_services": [
            "University plant health clinics and pathology diagnostic labs",
            "Subject matter specialist consultations in plant pathology and entomology",
            "Integrated Pest Management (IPM) packages of practices",
        ],
    },
    "when_to_contact": [
        {
            "id": "uncertain_diagnosis",
            "title": "Uncertain Visual Diagnosis (< 50% Confidence)",
            "guideline": "When model confidence is below 50% or symptoms overlap between multiple candidate diseases, physical inspection is essential before taking corrective action.",
        },
        {
            "id": "worsening_symptoms",
            "title": "Rapidly Spreading or Worsening Symptoms",
            "guideline": "If leaf lesions, yellowing, or wilting spreads rapidly across the field despite initial cultural sanitation practices.",
        },
        {
            "id": "recurring_outbreaks",
            "title": "Recurring Disease Outbreaks in Successive Seasons",
            "guideline": "Repeated infections suggest soil-borne inoculum, resistant disease strains, or micro-nutrient imbalances requiring laboratory soil/tissue testing.",
        },
        {
            "id": "pesticide_decisions",
            "title": "Chemical Pesticide Selection & Dosage Decisions",
            "guideline": "Never apply chemical fungicides or restricted pesticides without expert verification of active ingredient, recommended label dose, and waiting period.",
        },
    ],
    "disclaimer": (
        "CropCure AI provides preliminary computer-vision assessments. "
        "Automated visual predictions should never replace in-person physical crop inspection "
        "by qualified agricultural scientists, especially before applying restricted or chemical treatments."
    ),
}


@app.route("/experts/institutions", methods=["GET"])
def get_expert_institutions():
    """Return verified institutional support directory and national helpline info."""
    return jsonify({
        "status": "success",
        "institutions": EXPERT_INSTITUTIONS,
    }), 200


@app.route("/experts/search", methods=["GET"])
def search_local_experts():
    """Generate verified external directory and map queries for local KVKs and extension offices."""
    location = request.args.get("location", "").strip()

    if not location:
        return jsonify({
            "status": "error",
            "message": "Location parameter is required. Please provide a city, town, district, or PIN code."
        }), 400

    sanitized_location = urllib.parse.quote(location)

    google_maps_kvk = f"https://www.google.com/maps/search/?api=1&query=Krishi+Vigyan+Kendra+{sanitized_location}"
    google_maps_dept = f"https://www.google.com/maps/search/?api=1&query=District+Agriculture+Office+{sanitized_location}"
    osm_kvk = f"https://www.openstreetmap.org/search?query=Krishi+Vigyan+Kendra+{sanitized_location}"

    return jsonify({
        "status": "success",
        "location": location,
        "primary_links": {
            "google_maps_kvk": google_maps_kvk,
            "google_maps_dept": google_maps_dept,
            "openstreetmap_kvk": osm_kvk,
            "icar_kvk_portal": "https://kvk.icar.gov.in",
            "kisan_call_centre_portal": "https://farmer.gov.in",
        },
        "kisan_call_centre": {
            "toll_free_number": "1800-180-1551",
            "hours": "6:00 AM to 10:00 PM (All 7 Days)",
            "languages": "22 Indian languages",
        },
        "disclaimer": (
            "Local institution links launch verified external search queries on Google Maps and official ICAR portals. "
            "CropCure AI does not fabricate private expert credentials, phone numbers, or ratings. "
            "Always verify institutional affiliation and official credentials."
        ),
    }), 200


# =========================================
# Multilingual Support (Step 6)
# =========================================

@app.route("/languages", methods=["GET"])
def get_languages():
    """Return supported languages for CropCure AI."""
    return jsonify({
        "status": "success",
        "default": "en",
        "default_language": "en",
        "languages": [
            {"code": "en", "name": "English", "native_name": "English"},
            {"code": "te", "name": "Telugu", "native_name": "తెలుగు"},
            {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"},
        ]
    }), 200


# =========================================
# Start Server
# =========================================

if __name__ == "__main__":
    print("\nStarting CropCure AI Backend...")
    init_model()
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )