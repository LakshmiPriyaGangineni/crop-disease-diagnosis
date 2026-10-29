# CropCure AI: CNN-Based Crop Disease Diagnosis with Retrieval-Driven LLM Support

CropCure AI is an academic final-year B.Tech AIML major project designed to assist Indian farmers with leaf-level crop disease diagnosis and agronomically grounded guidance. The system integrates a PyTorch Convolutional Neural Network (CNN) for visual disease identification, a Retrieval-Augmented Generation (RAG) pipeline for domain-verified agricultural knowledge, and a multilingual interface supporting **English**, **Telugu (తెలుగు)**, and **Hindi (हिन्दी)**.

---

## Key Features

1. **Computer Vision Disease Diagnosis:**
   - Evaluates leaf images across 17 distinct disease and healthy classes covering Apple, Corn (Maize), Potato, and Tomato.
   - Provides predicted disease, visual confidence percentage, and top-3 candidate predictions.

2. **Uncertainty-Aware Safe Prediction:**
   - Detects when visual confidence drops below the 50% threshold.
   - Displays a prominent advisory banner and compares top candidate alternatives to prevent premature or incorrect chemical application.

3. **Retrieval-Augmented LLM Agricultural Guidance (RAG):**
   - Retrieves verified disease descriptions, symptoms, cultural treatments, and prevention measures from `rag/crop_data.json`.
   - Grounds responses using a server-side Groq LLM API without hallucinating unsupported treatments.

4. **Trilingual Farmer-Friendly Interface:**
   - Seamless language selector supporting English, Telugu, and Hindi across UI labels, disease names, symptoms, treatments, and AI chat.
   - Persistent language selection saved across sessions using `localStorage`.

5. **Dedicated Government Schemes Directory (`frontend/schemes.html`):**
   - Curated directory of verified central agricultural initiatives (PMFBY crop insurance, PM-KISAN, PMKSY irrigation, Kisan Credit Card, etc.) linking directly to official `.gov.in` and `.nic.in` portals.

6. **Nearby Agricultural Input Dealers (`frontend/shops.html`):**
   - Search utility for certified seeds, fertilizers, approved pesticides, and farm equipment by town or postal PIN code via verified Google Maps and OpenStreetMap queries.
   - Device location access is strictly optional; zero private geolocation data is saved or tracked.

7. **Agriculture Expert Support (`frontend/experts.html`):**
   - National Kisan Call Centre hotline (**1800-180-1551**, 6:00 AM – 10:00 PM, 22 languages).
   - Direct search for district Krishi Vigyan Kendras (KVKs) and State Agriculture Departments.
   - Interactive Consultation Summary Generator with one-click clipboard copying for sharing diagnostic context with agronomists.

8. **Dedicated Technical Model Performance Section (`frontend/performance.html`):**
   - Segregated technical view for researchers and project evaluators displaying overall accuracy, top-3 accuracy, macro/weighted metrics, per-class performance tables, and confusion matrix.

---

## Supported Crops and Disease Classes (17 Classes)

| Crop | Supported Classes |
|---|---|
| **Apple** | Apple Scab, Apple Rust, Apple (Healthy) |
| **Corn (Maize)** | Corn Gray Leaf Spot, Corn Leaf Blight, Corn Leaf Rust |
| **Potato** | Potato Early Blight, Potato Late Blight, Potato Leaf Blight, Potato Leafroll Virus, Potato (Healthy) |
| **Tomato** | Tomato Bacterial Spot, Tomato Early Blight, Tomato Late Blight, Tomato Leaf Mold, Tomato Septoria Leaf Spot, Tomato (Healthy) |

---

## System Architecture

```
[ Farmer Web UI (HTML5 / Vanilla CSS / ES6 JS) ]
      │                               ▲
      │ (Multipart / JSON HTTP)       │ (Localized JSON Response)
      ▼                               │
[ Flask Backend API (backend/app.py) ]
      ├──> [ CNN Inference Engine (inference/cnn_inference.py) ]
      │         └── PyTorch Model Weights (models/best_model.pth)
      │
      ├──> [ RAG Knowledge Retriever (rag/retriever.py) ]
      │         └── Verified Knowledge Base (rag/crop_data.json)
      │
      └──> [ Grounded LLM Service (rag/llm_service.py) ]
                └── Groq API Server-Side Call (GROQ_API_KEY from .env)
```

---

## Model Evaluation & Performance (Source of Truth)

Metrics evaluated on the holdout unified test split of **1,903 test images** (`results/cnn_evaluation/test_metrics.json`):

- **Overall Test Accuracy:** 84.92% (1,616 / 1,903 correct)
- **Top-3 Accuracy:** 94.38%
- **Macro Average:** Precision = 0.6114, Recall = 0.6025, F1-Score = 0.5896
- **Weighted Average:** Precision = 0.8562, Recall = 0.8492, F1-Score = 0.8492
- Detailed per-class breakdowns and confusion matrix are available on the Model Performance page (`frontend/performance.html`) or in `results/cnn_evaluation/`.

---

## Installation & Setup Instructions (Windows)

### 1. Prerequisites
- **Python 3.10 – 3.12** installed and added to `PATH`.
- **Node.js** (optional, for running client-side test scripts).
- Git.

### 2. Clone and Setup Environment
```powershell
# Navigate to the project directory
cd C:\Users\user\OneDrive\Desktop\major_project

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
.venv\Scripts\Activate.ps1
```

### 3. Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Secrets
Create a local `.env` file in the project root by copying the template:
```powershell
copy .env.example .env
```
Open `.env` and add your Groq API key:
```ini
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```
*(Note: `.env` is ignored by Git and must never be committed to public repositories).*

### 5. Model Weights Setup
Place the trained model weights file `best_model.pth` (generated from training via `python training/train_cnn.py` or retrieved from project model storage) in the `models/` directory:
```
models/
  └── best_model.pth
```
*(Trained `.pth` binary files are excluded from Git via `.gitignore` to keep the repository lightweight).*

---

## Running the Application

### 1. Start the Flask Backend
```powershell
python backend/app.py
```
The backend server runs locally at `http://127.0.0.1:5000`.

### 2. Open the Frontend
Open `frontend/index.html` directly in any modern web browser, or serve it using Python's static server:
```powershell
python -m http.server 3000 --directory frontend
```
Then visit `http://127.0.0.1:3000` in your browser.

---

## Running Tests

Run the full integration test suite (42 tests covering CNN prediction, uncertainty handling, RAG retrieval, schemes, shops, multilingual support, and expert support):
```powershell
python backend/test_integration.py
```

Run the end-to-end frontend data flow simulation:
```powershell
python backend/test_frontend_flow.py
```

Verify JavaScript syntax:
```powershell
node -c frontend/script.js
node -c frontend/translations.js
```

---

## Files Excluded from Version Control (`.gitignore`)

The following files are strictly excluded from the Git repository:
- `.env` (contains sensitive API keys).
- `.venv/`, `venv/` (Python virtual environment directories).
- `models/*.pth` (large binary model weights).
- `datasets/`, `data/` (raw training/test image sets).
- `rag/faiss_index.bin` (locally generated vector cache).
- `*.log`, `__pycache__/`, `.pytest_cache/` (runtime logs and compiled bytecode).

The structured domain knowledge bases (`rag/crop_data.json` and `rag/government_schemes.json`) are lightweight and tracked in the repository.

---

## Limitations and Agronomic Notice

1. **Preliminary Machine Assessment:** CNN predictions are visual estimates based on training distributions. Real-world field conditions (shadows, background foliage, multiple co-occurring pathogens) can reduce confidence.
2. **Mandatory Expert Confirmation:** Diagnoses with confidence below 50% must be treated as provisional. Farmers should verify symptoms against candidate descriptions or consult a local Krishi Vigyan Kendra (KVK) scientist before taking action.
3. **No Automated Chemical Prescriptions:** CropCure AI does not automatically prescribe chemical dosages or spray schedules. Farmers must seek physical confirmation from local agricultural officers before purchasing or applying synthetic fungicides or pesticides.
4. **Helpline Operating Hours:** The national Kisan Call Centre (**1800-180-1551**) operates from 6:00 AM to 10:00 PM; farmers should verify regional language staffing through official channels.

---

## Academic Disclaimer
This project was developed as a final-year B.Tech Major Project in Artificial Intelligence & Machine Learning (AIML). It is intended for educational, research, and advisory support purposes.
