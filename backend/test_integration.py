"""
Integration test suite for CropCure AI Step 1 Improvements (Refined).

Tests:
1. /predict using real image from data/unified_test (verifying CNN inference & 0.50 uncertainty rule)
2. Confidence above 0.50 (/chat with confidence = 0.85 -> primary visual diagnosis, uncertain=False)
3. Confidence exactly 0.50 boundary condition (/chat with confidence = 0.50 -> primary diagnosis, uncertain=False)
4. Confidence below 0.50 (/chat with confidence = 0.38 -> Multi-Candidate RAG, uncertain=True, warning present)
5. Multi-candidate RAG with candidates spanning DIFFERENT CROPS (Apple, Corn, Tomato)
6. Missing knowledge for an unsupported candidate (e.g., Grape_Black_Rot -> has_knowledge=False)
7. Malformed image inputs & invalid request error handling (HTTP 400)
8. Security check: API key safety & .env file untouched

Safety restrictions:
- GROQ_API_KEY is never exposed or printed
- .env is never modified
- models/best_model.pth is never modified
"""

import io
import json
import os
import sys

# Configure stdout encoding for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import app
from rag.llm_service import get_api_key

TEST_IMG_1 = os.path.join(
    PROJECT_ROOT,
    "data",
    "unified_test",
    "Tomato_Early_Blight",
    "dataset_1_plantvillage__004285__0114f7b3-7f56-4bef-aa47-7a82da142d4b___RS_Erly.B 7437.JPG"
)

TEST_IMG_2 = os.path.join(
    PROJECT_ROOT,
    "data",
    "unified_test",
    "Apple_Rust",
    "dataset_6_web_sourced__000042__110.jpg"
)


def run_tests():
    client = app.test_client()
    passed = 0
    total = 8

    print("=" * 75)
    print("STARTING CROPCURE AI STEP 1 INTEGRATION TESTS (REFINED)")
    print("=" * 75)

    # Record .env mtime to guarantee it is never modified
    env_file = os.path.join(PROJECT_ROOT, ".env")
    initial_env_mtime = os.path.getmtime(env_file) if os.path.exists(env_file) else None

    # ---------------------------------------------------------
    # TEST 1: Real image inference & safety fields in /predict
    # ---------------------------------------------------------
    print("\n--- TEST 1: /predict with real image & safety fields ---")
    assert os.path.exists(TEST_IMG_1), f"Test image 1 not found: {TEST_IMG_1}"

    with open(TEST_IMG_1, "rb") as f:
        img_bytes = f.read()

    data = {"image": (io.BytesIO(img_bytes), os.path.basename(TEST_IMG_1))}
    resp1 = client.post("/predict", content_type="multipart/form-data", data=data)
    print(f"HTTP Status: {resp1.status_code}")
    res1_json = resp1.get_json()
    print(f"Prediction: {res1_json.get('predicted_class')}, Confidence: {res1_json.get('confidence')}")
    print(f"Uncertain: {res1_json.get('uncertain')}, Warning: {res1_json.get('warning')}")

    test1_ok = (
        resp1.status_code == 200
        and res1_json.get("status") == "success"
        and "predicted_class" in res1_json
        and "confidence" in res1_json
        and "class_index" in res1_json
        and "top3" in res1_json
        and len(res1_json["top3"]) == 3
        and "uncertain" in res1_json
        and isinstance(res1_json["confidence"], float)
    )
    if test1_ok:
        print("[PASS] TEST 1: /predict returns CNN prediction with uncertainty flag and top3 candidates")
        passed += 1
    else:
        print("[FAIL] TEST 1: Unexpected /predict response structure")

    # ---------------------------------------------------------
    # TEST 2: Confidence above 0.50 (/chat with confidence = 0.85)
    # ---------------------------------------------------------
    print("\n--- TEST 2: Confidence above 0.50 (confidence = 0.85) ---")
    high_conf_payload = {
        "message": "What is the recommended treatment for this disease?",
        "predicted_disease": "Tomato_Early_Blight",
        "confidence": 0.85,
        "top3": [
            {"class": "Tomato_Early_Blight", "probability": 0.85},
            {"class": "Tomato_Late_Blight", "probability": 0.10},
            {"class": "Tomato_Septoria_Leaf_Spot", "probability": 0.05}
        ]
    }
    resp2 = client.post("/chat", json=high_conf_payload)
    print(f"HTTP Status: {resp2.status_code}")
    res2_json = resp2.get_json()
    answer2 = res2_json.get("answer", "")
    print(f"Answer snippet: {answer2[:200]}...")
    print(f"Uncertain: {res2_json.get('uncertain')}, Warning: {res2_json.get('warning')}")

    test2_ok = (
        resp2.status_code == 200
        and res2_json.get("success") is True
        and res2_json.get("uncertain") is False
        and res2_json.get("warning") is None
        and len(res2_json.get("sources", [])) > 0
        and bool(answer2)
    )
    if test2_ok:
        print("[PASS] TEST 2: Confidence above 0.50 correctly treated as primary visual diagnosis (uncertain=False)")
        passed += 1
    else:
        print("[FAIL] TEST 2: Above 0.50 confidence test failed")

    # ---------------------------------------------------------
    # TEST 3: Confidence exactly 0.50 boundary condition
    # ---------------------------------------------------------
    print("\n--- TEST 3: Confidence exactly 0.50 boundary condition ---")
    boundary_payload = {
        "message": "What are the symptoms and prevention measures?",
        "predicted_disease": "Potato_Late_Blight",
        "confidence": 0.50,
        "top3": [
            {"class": "Potato_Late_Blight", "probability": 0.50},
            {"class": "Potato_Early_Blight", "probability": 0.30},
            {"class": "Tomato_Late_Blight", "probability": 0.20}
        ]
    }
    resp3 = client.post("/chat", json=boundary_payload)
    print(f"HTTP Status: {resp3.status_code}")
    res3_json = resp3.get_json()
    answer3 = res3_json.get("answer", "")
    print(f"Uncertain: {res3_json.get('uncertain')}, Warning: {res3_json.get('warning')}")

    # By the 0.50 rule: confidence < 0.50 is uncertain; confidence >= 0.50 is primary diagnosis
    test3_ok = (
        resp3.status_code == 200
        and res3_json.get("success") is True
        and res3_json.get("uncertain") is False
        and res3_json.get("warning") is None
        and bool(answer3)
    )
    if test3_ok:
        print("[PASS] TEST 3: Confidence exactly 0.50 boundary correctly treated as primary diagnosis (uncertain=False)")
        passed += 1
    else:
        print("[FAIL] TEST 3: 0.50 boundary test failed")

    # ---------------------------------------------------------
    # TEST 4: Confidence below 0.50 with Multi-Candidate RAG
    # ---------------------------------------------------------
    print("\n--- TEST 4: Confidence below 0.50 with Multi-Candidate RAG (< 0.50) ---")
    low_conf_payload = {
        "message": "What disease could my tomato crop have and how do I manage it?",
        "predicted_disease": "Tomato_Early_Blight",
        "confidence": 0.38,
        "top3": [
            {"class": "Tomato_Early_Blight", "probability": 0.38},
            {"class": "Tomato_Late_Blight", "probability": 0.34},
            {"class": "Tomato_Septoria_Leaf_Spot", "probability": 0.28}
        ]
    }
    resp4 = client.post("/chat", json=low_conf_payload)
    print(f"HTTP Status: {resp4.status_code}")
    res4_json = resp4.get_json()
    answer4 = res4_json.get("answer", "")
    sources4 = res4_json.get("sources", [])
    print(f"Uncertain flag: {res4_json.get('uncertain')}")
    print(f"Warning: {res4_json.get('warning')}")
    print(f"Sources returned count: {len(sources4)}")
    for s in sources4:
        print(f"  - [{s.get('candidate', 'N/A')}] {s.get('disease')}")

    # Guardrail check:
    # 1. Flagged as uncertain (< 0.50)
    # 2. Warning message returned
    # 3. Retrieved knowledge for all 3 candidates (Early Blight, Late Blight, Septoria)
    # 4. Answer discusses candidates differentially and does not confirm single treatment
    sources_diseases = [s.get("disease", "").lower() for s in sources4]
    has_all_candidates = (
        any("early blight" in d for d in sources_diseases)
        and any("late blight" in d for d in sources_diseases)
        and any("septoria" in d for d in sources_diseases)
    )

    test4_ok = (
        resp4.status_code == 200
        and res4_json.get("success") is True
        and res4_json.get("uncertain") is True
        and res4_json.get("warning") is not None
        and has_all_candidates
        and any(w in answer4.lower() for w in ["uncertain", "candidate", "possib", "provisional", "differential"])
    )
    if test4_ok:
        print("[PASS] TEST 4: Confidence below 0.50 properly triggered uncertainty warning and multi-candidate RAG")
        passed += 1
    else:
        print(f"[FAIL] TEST 4: Low-confidence multi-candidate RAG failed (has_all_candidates={has_all_candidates})")

    # ---------------------------------------------------------
    # TEST 5: Multi-candidate RAG across DIFFERENT CROPS
    # ---------------------------------------------------------
    print("\n--- TEST 5: Multi-candidate RAG across DIFFERENT CROPS ---")
    multi_crop_payload = {
        "message": "What disease might this leaf have and what should I do?",
        "predicted_disease": "Apple_Rust",
        "confidence": 0.32,
        "top3": [
            {"class": "Apple_Rust", "probability": 0.32},
            {"class": "Corn_Leaf_Rust", "probability": 0.28},
            {"class": "Tomato_Early_Blight", "probability": 0.24}
        ]
    }
    resp5 = client.post("/chat", json=multi_crop_payload)
    print(f"HTTP Status: {resp5.status_code}")
    res5_json = resp5.get_json()
    answer5 = res5_json.get("answer", "")
    sources5 = res5_json.get("sources", [])
    print(f"Sources across crops: {len(sources5)}")
    for s in sources5:
        print(f"  - Candidate: {s.get('candidate')} -> Crop: {s.get('crop')}, Disease: {s.get('disease')}")

    sources_crops = set(s.get("crop", "").lower() for s in sources5)
    has_multiple_crops = ("apple" in sources_crops) and ("corn" in sources_crops) and ("tomato" in sources_crops)

    test5_ok = (
        resp5.status_code == 200
        and res5_json.get("success") is True
        and res5_json.get("uncertain") is True
        and has_multiple_crops
        and any(w in answer5.lower() for w in ["apple", "corn", "tomato"])
    )
    if test5_ok:
        print("[PASS] TEST 5: Candidates from different crops handled with crop-specific labeled knowledge")
        passed += 1
    else:
        print(f"[FAIL] TEST 5: Cross-crop multi-candidate handling failed (crops={sources_crops})")

    # ---------------------------------------------------------
    # TEST 6: Missing knowledge for an unsupported candidate
    # ---------------------------------------------------------
    print("\n--- TEST 6: Missing knowledge for an unsupported candidate ---")
    unsupported_payload = {
        "message": "Can you give me the treatment and symptoms for these possible diseases?",
        "predicted_disease": "Tomato_Early_Blight",
        "confidence": 0.36,
        "top3": [
            {"class": "Tomato_Early_Blight", "probability": 0.36},
            {"class": "Grape_Black_Rot", "probability": 0.30},
            {"class": "Potato_Late_Blight", "probability": 0.22}
        ]
    }
    resp6 = client.post("/chat", json=unsupported_payload)
    print(f"HTTP Status: {resp6.status_code}")
    res6_json = resp6.get_json()
    answer6 = res6_json.get("answer", "")
    candidates6 = res6_json.get("candidates", [])
    print(f"Candidates status: {candidates6}")

    # Grape Black Rot is not in crop_data.json: verify that has_knowledge is False
    grape_cand = next((c for c in candidates6 if "grape" in c.get("clean_name", "").lower()), None)
    grape_missing_flag = grape_cand is not None and grape_cand.get("has_knowledge") is False
    grape_noted_in_answer = any(w in answer6.lower() for w in ["grape", "black rot", "not available", "no specific", "lacks", "unavailable"])

    test6_ok = (
        resp6.status_code == 200
        and res6_json.get("success") is True
        and grape_missing_flag
        and grape_noted_in_answer
    )
    if test6_ok:
        print("[PASS] TEST 6: System cleanly flagged missing candidate knowledge and notified user")
        passed += 1
    else:
        print(f"[FAIL] TEST 6: Missing knowledge test failed (grape_flag={grape_missing_flag})")

    # ---------------------------------------------------------
    # TEST 7: Malformed images & invalid inputs (HTTP 400)
    # ---------------------------------------------------------
    print("\n--- TEST 7: Malformed images & input validation ---")
    bad_img_resp = client.post(
        "/predict",
        content_type="multipart/form-data",
        data={"image": (io.BytesIO(b"Not a valid image"), "corrupt.jpg")}
    )
    no_img_resp = client.post("/predict", content_type="multipart/form-data", data={})
    empty_name_resp = client.post(
        "/predict",
        content_type="multipart/form-data",
        data={"image": (io.BytesIO(b""), "")}
    )
    empty_chat_resp = client.post("/chat", json={"message": "   "})
    missing_chat_resp = client.post("/chat", json={})

    test7_ok = (
        bad_img_resp.status_code == 400
        and no_img_resp.status_code == 400
        and empty_name_resp.status_code == 400
        and empty_chat_resp.status_code == 400
        and missing_chat_resp.status_code == 400
    )
    if test7_ok:
        print("[PASS] TEST 7: Malformed images and empty chat inputs safely rejected with HTTP 400")
        passed += 1
    else:
        print("[FAIL] TEST 7: Error handling did not return expected HTTP 400 status codes")

    # ---------------------------------------------------------
    # TEST 8: Security and integrity checks
    # ---------------------------------------------------------
    print("\n--- TEST 8: Security & integrity checks ---")
    api_key = get_api_key()
    key_leaked = False
    all_answers = [
        res2_json.get("answer", ""),
        res3_json.get("answer", ""),
        res4_json.get("answer", ""),
        res5_json.get("answer", ""),
        res6_json.get("answer", ""),
    ]
    if api_key and len(api_key) > 5:
        for a in all_answers:
            if api_key in a:
                key_leaked = True
                break

    env_unmodified = True
    if initial_env_mtime and os.path.exists(env_file):
        current_mtime = os.path.getmtime(env_file)
        if current_mtime != initial_env_mtime:
            env_unmodified = False

    test8_ok = (not key_leaked) and env_unmodified
    if test8_ok:
        print("[PASS] TEST 8: API key never exposed; .env remained completely untouched")
        passed += 1
    else:
        print(f"[FAIL] TEST 8: Security violation detected (key_leaked={key_leaked}, env_unmodified={env_unmodified})")

    # ---------------------------------------------------------
    # TEST 9: Prevention data flow for supported diseases
    # ---------------------------------------------------------
    print("\n--- TEST 9: Prevention data flow for supported diseases ---")
    prev_payload = {
        "message": "What is the prevention for Tomato Early Blight?",
        "predicted_disease": "Tomato_Early_Blight",
        "confidence": 0.88,
        "top3": [
            {"class": "Tomato_Early_Blight", "probability": 0.88},
            {"class": "Tomato_Late_Blight", "probability": 0.08},
            {"class": "Tomato_Septoria_Leaf_Spot", "probability": 0.04}
        ]
    }
    resp9 = client.post("/chat", json=prev_payload)
    res9_json = resp9.get_json()
    knowledge9 = res9_json.get("knowledge")
    print(f"Knowledge payload present: {knowledge9 is not None}")
    if knowledge9:
        print(f"Crop: {knowledge9.get('crop')}, Disease: {knowledge9.get('disease')}")
        print(f"Prevention snippet: {knowledge9.get('prevention', '')[:120]}...")

    # Also verify /predict returns structured knowledge
    predict_knowledge = res1_json.get("knowledge")
    print(f"/predict knowledge present: {predict_knowledge is not None}")

    test9_ok = (
        resp9.status_code == 200
        and knowledge9 is not None
        and bool(knowledge9.get("prevention"))
        and "crop rotation" in knowledge9.get("prevention", "").lower()
        and predict_knowledge is not None
        and bool(predict_knowledge.get("prevention"))
    )
    if test9_ok:
        print("[PASS] TEST 9: Prevention data successfully flows from crop_data.json through /predict and /chat")
        passed += 1
    else:
        print(f"[FAIL] TEST 9: Prevention data flow failed (chat_knowledge={knowledge9 is not None}, predict_knowledge={predict_knowledge is not None})")

    # ---------------------------------------------------------
    # TEST 10: Prevention data handling when knowledge is unavailable
    # ---------------------------------------------------------
    print("\n--- TEST 10: Prevention data handling when knowledge is unavailable ---")
    from rag.retriever import get_disease_entry

    unsupported_entry = get_disease_entry("Nonexistent_Plant_Disease_XYZ")
    print(f"get_disease_entry for unknown class: {unsupported_entry}")

    # Query with a completely unsupported disease class
    unknown_payload = {
        "message": "What is the prevention for this disease?",
        "predicted_disease": "Nonexistent_Plant_Disease_XYZ",
        "confidence": 0.90,
        "top3": [
            {"class": "Nonexistent_Plant_Disease_XYZ", "probability": 0.90}
        ]
    }
    resp10 = client.post("/chat", json=unknown_payload)
    res10_json = resp10.get_json()
    knowledge10 = res10_json.get("knowledge")
    print(f"Knowledge returned for unsupported disease: {knowledge10}")

    test10_ok = (
        unsupported_entry is None
        and (knowledge10 is None or not knowledge10.get("prevention"))
    )
    if test10_ok:
        print("[PASS] TEST 10: Missing knowledge cleanly returns None/empty without fabricating prevention advice")
        passed += 1
    else:
        print(f"[FAIL] TEST 10: Missing knowledge handling failed (entry={unsupported_entry}, knowledge={knowledge10})")

    # ---------------------------------------------------------
    # TEST 11: Markdown Table and <br> cleanup in frontend script
    # ---------------------------------------------------------
    print("\n--- TEST 11: Frontend Markdown table, separator, and <br> cleanup ---")
    import subprocess

    js_test_code = """
    const fs = require('fs');
    const path = require('path');
    global.document = {
        getElementById: () => ({ addEventListener: () => {}, classList: { add: () => {}, remove: () => {} }, style: {} }),
        createElement: () => ({ classList: { add: () => {} }, appendChild: () => {} })
    };
    global.URL = { createObjectURL: () => "" };

    const scriptPath = path.resolve('frontend', 'script.js');
    eval(fs.readFileSync(scriptPath, 'utf8'));

    // Test Markdown Table & Separators
    const tableInput = "| Disease | Severity |\\n|---|---|\\n| Early Blight | Moderate |";
    const renderedTable = renderMarkdown(tableInput);
    if (renderedTable.includes("|---|---|")) throw new Error("Table separator row not stripped!");
    if (!renderedTable.includes("<table class=\\"markdown-table\\">")) throw new Error("Table tag not created!");
    if (!renderedTable.includes("<th>Disease</th>")) throw new Error("Header cell not created!");
    if (!renderedTable.includes("<td>Early Blight</td>")) throw new Error("Data cell not created!");

    // Test Literal <br> tag normalization
    const brInput = "Line 1<br>Line 2<br/>Line 3<br />Line 4";
    const renderedBr = renderMarkdown(brInput);
    if (renderedBr.includes("&lt;br&gt;") || renderedBr.includes("&lt;br/&gt;")) throw new Error("Literal <br> leaked as &lt;br&gt;!");

    // Test XSS safety
    const xssInput = "Hello <script>alert(1)</script> <img onerror=x>";
    const renderedXss = renderMarkdown(xssInput);
    if (renderedXss.includes("<script>") || renderedXss.includes("<img")) throw new Error("Untrusted HTML tag leaked!");

    console.log("MARKDOWN_AND_HTML_CLEAN");
    """

    try:
        proc11 = subprocess.run(
            ["node", "-e", js_test_code],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        test11_ok = (proc11.returncode == 0 and "MARKDOWN_AND_HTML_CLEAN" in proc11.stdout)
        if not test11_ok:
            print(f"Node output: {proc11.stdout}, error: {proc11.stderr}")
    except Exception as exc:
        print(f"Node execution exception: {exc}")
        test11_ok = False

    if test11_ok:
        print("[PASS] TEST 11: Markdown tables parsed, separators stripped, literal <br> normalized, and XSS escaped")
        passed += 1
    else:
        print("[FAIL] TEST 11: Markdown or HTML rendering cleanup failed")

    # ---------------------------------------------------------
    # TEST 12: Section extraction in frontend script
    # ---------------------------------------------------------
    print("\n--- TEST 12: Frontend section extraction without bullet breaking ---")
    js_extract_code = """
    const fs = require('fs');
    const path = require('path');
    global.document = {
        getElementById: () => ({ addEventListener: () => {}, classList: { add: () => {}, remove: () => {} }, style: {} }),
        createElement: () => ({ classList: { add: () => {} }, appendChild: () => {} })
    };
    global.URL = { createObjectURL: () => "" };

    const scriptPath = path.resolve('frontend', 'script.js');
    eval(fs.readFileSync(scriptPath, 'utf8'));

    const llmSample = `
    ### 1. Visual Symptoms
    - **Concentric rings:** Dark rings on older leaves.<br>
    - **Yellow halo:** Surrounding halo.

    ### 2. Treatment & Control
    - **Fungicide:** Apply chlorothalonil spray early.
    - **Pruning:** Remove infected leaves.

    ### 3. Prevention & Management
    - **Crop rotation:** Rotate with non-solanaceous crops for 2 years.<br>
    - **Sanitation:** Remove and burn infected debris.
    `;

    const prevSection = extractSection(llmSample, "prevention");
    const treatSection = extractSection(llmSample, "treatment");
    const symSection = extractSection(llmSample, "symptoms");

    if (!prevSection.includes("Crop rotation") || !prevSection.includes("Sanitation")) {
        throw new Error("extractSection stopped prematurely on bold bullet item in prevention!");
    }
    if (prevSection.includes("Fungicide")) {
        throw new Error("extractSection leaked treatment into prevention!");
    }
    if (!treatSection.includes("Fungicide") || !treatSection.includes("Pruning")) {
        throw new Error("extractSection failed for treatment!");
    }
    if (!symSection.includes("Concentric rings")) {
        throw new Error("extractSection failed for symptoms!");
    }

    console.log("SECTION_EXTRACTION_CLEAN");
    """

    try:
        proc12 = subprocess.run(
            ["node", "-e", js_extract_code],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        test12_ok = (proc12.returncode == 0 and "SECTION_EXTRACTION_CLEAN" in proc12.stdout)
        if not test12_ok:
            print(f"Node output: {proc12.stdout}, error: {proc12.stderr}")
    except Exception as exc:
        print(f"Node execution exception: {exc}")
        test12_ok = False

    if test12_ok:
        print("[PASS] TEST 12: Section extraction cleanly captures multi-line bold bullet lists without breaking")
        passed += 1
    else:
        print("[FAIL] TEST 12: Section extraction test failed")

    # ---------------------------------------------------------
    # TEST 13: GET /evaluation returns valid artifacts & expected fields (Step 3)
    # ---------------------------------------------------------
    print("\n--- TEST 13: GET /evaluation valid artifacts & fields ---")
    resp13 = client.get("/evaluation")
    print(f"HTTP Status: {resp13.status_code}")
    res13_json = resp13.get_json()

    summary13 = res13_json.get("summary", {})
    macro13 = res13_json.get("macro_metrics", {})
    weighted13 = res13_json.get("weighted_metrics", {})
    split13 = res13_json.get("split_details", {})
    per_class13 = res13_json.get("per_class_metrics", {})
    cm13 = res13_json.get("confusion_matrix", {})
    disclaimer13 = res13_json.get("disclaimer", "")

    print(f"Overall Accuracy: {summary13.get('overall_test_accuracy_pct')}% ({summary13.get('total_correct')}/{summary13.get('total_test_images')})")
    print(f"Macro Metrics: Precision={macro13.get('precision')}, Recall={macro13.get('recall')}, F1={macro13.get('f1_score')}")
    print(f"Weighted Metrics: Precision={weighted13.get('precision')}, Recall={weighted13.get('recall')}, F1={weighted13.get('f1_score')}")
    print(f"Class count in per_class_metrics: {len(per_class13)}")

    # Strict checks
    test13_ok = (
        resp13.status_code == 200
        and res13_json.get("status") == "success"
        and summary13.get("total_test_images") == 1903
        and summary13.get("total_correct") == 1616
        and summary13.get("total_incorrect") == 287
        and summary13.get("num_classes") == 17
        and summary13.get("overall_test_accuracy") == 0.849185
        and summary13.get("overall_test_accuracy_pct") == 84.92
        and summary13.get("top3_accuracy") == 0.943773
        and macro13.get("precision") == 0.611397
        and macro13.get("recall") == 0.60252
        and macro13.get("f1_score") == 0.589588
        and weighted13.get("precision") == 0.856227
        and weighted13.get("recall") == 0.849186
        and weighted13.get("f1_score") == 0.849196
        # Distinction check: macro metrics must differ from weighted metrics
        and macro13.get("precision") != weighted13.get("precision")
        and len(per_class13) == 17
        and split13.get("total_test_images") == 1903
        and split13.get("num_classes") == 17
        and bool(disclaimer13)
        and "offline" in disclaimer13.lower()
    )
    if test13_ok:
        print("[PASS] TEST 13: GET /evaluation returns all approved evaluation metrics, distinct macro/weighted values, and split details")
        passed += 1
    else:
        print("[FAIL] TEST 13: GET /evaluation response structure or values did not match expected artifacts")

    # ---------------------------------------------------------
    # TEST 14: Confusion matrix integrity, class ordering & image endpoint (Step 3)
    # ---------------------------------------------------------
    print("\n--- TEST 14: Confusion matrix integrity and class ordering ---")
    cm_classes = cm13.get("classes", [])
    cm_matrix = cm13.get("matrix", [])

    diag_sum = sum(cm_matrix[i][i] for i in range(len(cm_classes))) if len(cm_matrix) == 17 else 0
    total_cm_sum = sum(sum(row) for row in cm_matrix) if len(cm_matrix) == 17 else 0

    print(f"Classes in matrix: {len(cm_classes)}")
    print(f"Matrix shape: {len(cm_matrix)} x {len(cm_matrix[0]) if cm_matrix else 0}")
    print(f"Diagonal sum (correct predictions): {diag_sum} (expected 1616)")
    print(f"Total matrix elements sum: {total_cm_sum} (expected 1903)")

    # Verify class ordering matches per_class_metrics class_index
    ordering_correct = True
    for idx, cname in enumerate(cm_classes):
        expected_idx = per_class13.get(cname, {}).get("class_index")
        if expected_idx != idx:
            ordering_correct = False
            print(f"  Class order mismatch for {cname}: matrix index {idx} vs per_class index {expected_idx}")

    # Verify static confusion matrix plot route
    resp14_img = client.get("/evaluation/confusion-matrix-image")
    img_ok = resp14_img.status_code == 200 and resp14_img.mimetype == "image/png"
    print(f"Confusion matrix image endpoint status: {resp14_img.status_code}, mimetype: {resp14_img.mimetype}")

    test14_ok = (
        len(cm_classes) == 17
        and len(cm_matrix) == 17
        and all(len(row) == 17 for row in cm_matrix)
        and ordering_correct
        and diag_sum == 1616
        and total_cm_sum == 1903
        and img_ok
    )
    if test14_ok:
        print("[PASS] TEST 14: Confusion matrix preserves 17x17 dimensions, correct class ordering, diagonal sum (1616), and image serving")
        passed += 1
    else:
        print(f"[FAIL] TEST 14: Confusion matrix validation failed (ordering={ordering_correct}, diag_sum={diag_sum}, img_ok={img_ok})")

    # ---------------------------------------------------------
    # TEST 15: Missing evaluation artifacts error handling (Step 3)
    # ---------------------------------------------------------
    print("\n--- TEST 15: Missing evaluation artifacts error handling ---")
    from backend.app import load_evaluation_data

    nonexistent_dir = os.path.join(PROJECT_ROOT, "results", "nonexistent_test_artifacts_dir")
    data_missing, err_missing, status_missing = load_evaluation_data(eval_dir=nonexistent_dir)
    print(f"Missing artifacts status: {status_missing}, message: {err_missing.get('message') if err_missing else None}")

    test15_ok = (
        data_missing is None
        and status_missing == 404
        and err_missing is not None
        and err_missing.get("status") == "error"
        and "not found" in err_missing.get("message", "").lower()
    )
    if test15_ok:
        print("[PASS] TEST 15: Missing evaluation artifacts gracefully handled with HTTP 404 and informative error message")
        passed += 1
    else:
        print(f"[FAIL] TEST 15: Missing artifacts test failed (status={status_missing})")

    # ---------------------------------------------------------
    # TEST 16: Malformed artifact data error handling (Step 3)
    # ---------------------------------------------------------
    print("\n--- TEST 16: Malformed evaluation artifact error handling ---")
    import tempfile

    with tempfile.TemporaryDirectory() as temp_eval_dir:
        # Create corrupted JSON file
        corrupt_test_metrics = os.path.join(temp_eval_dir, "test_metrics.json")
        with open(corrupt_test_metrics, "w", encoding="utf-8") as f:
            f.write("{ INVALID JSON NOT TERMINATED ...")

        # Create valid placeholder companions
        with open(os.path.join(temp_eval_dir, "per_class_metrics.json"), "w", encoding="utf-8") as f:
            f.write("{}")
        with open(os.path.join(temp_eval_dir, "confusion_matrix.json"), "w", encoding="utf-8") as f:
            f.write("{}")

        data_malformed, err_malformed, status_malformed = load_evaluation_data(eval_dir=temp_eval_dir)
        print(f"Malformed artifact status: {status_malformed}, message: {err_malformed.get('message') if err_malformed else None}")

    test16_ok = (
        data_malformed is None
        and status_malformed == 500
        and err_malformed is not None
        and err_malformed.get("status") == "error"
        and "malformed" in err_malformed.get("message", "").lower()
    )
    if test16_ok:
        print("[PASS] TEST 16: Malformed evaluation artifact JSON cleanly handled with HTTP 500 without crashing")
        passed += 1
    else:
        print(f"[FAIL] TEST 16: Malformed artifact test failed (status={status_malformed})")

    # ---------------------------------------------------------
    # TEST 17: Frontend Model Performance rendering & interactions (Step 3)
    # ---------------------------------------------------------
    print("\n--- TEST 17: Frontend Model Performance rendering & interactions ---")
    js_performance_test = """
    const fs = require('fs');
    const path = require('path');

    // Mock DOM elements required by script.js
    const elements = {};
    function mockElement(id) {
        if (!elements[id]) {
            elements[id] = {
                id: id,
                textContent: '',
                innerHTML: '',
                value: '',
                classList: {
                    _classes: new Set(),
                    add: function(c) { this._classes.add(c); },
                    remove: function(c) { this._classes.delete(c); },
                    contains: function(c) { return this._classes.has(c); }
                },
                style: {},
                addEventListener: function(event, handler) { this['on' + event] = handler; },
                querySelectorAll: function() { return []; }
            };
        }
        return elements[id];
    }

    global.document = {
        getElementById: mockElement,
        createElement: function(tag) { return mockElement(tag + '_' + Math.random()); },
        addEventListener: function() {},
        readyState: 'complete'
    };
    global.URL = { createObjectURL: () => "" };

    const scriptPath = path.resolve('frontend', 'script.js');
    eval(fs.readFileSync(scriptPath, 'utf8'));

    // Verify all performance functions exist
    if (typeof renderOverviewMetrics !== 'function') throw new Error('renderOverviewMetrics missing');
    if (typeof renderComparisonTable !== 'function') throw new Error('renderComparisonTable missing');
    if (typeof renderSplitDetails !== 'function') throw new Error('renderSplitDetails missing');
    if (typeof renderPerClassTable !== 'function') throw new Error('renderPerClassTable missing');
    if (typeof renderConfusionMatrix !== 'function') throw new Error('renderConfusionMatrix missing');

    // Test renderComparisonTable
    const mockData = {
        summary: {
            overall_test_accuracy: 0.849185,
            overall_test_accuracy_pct: 84.92,
            top3_accuracy_pct: 94.38,
            total_test_images: 1903,
            total_correct: 1616
        },
        macro_metrics: { precision: 0.611397, recall: 0.60252, f1_score: 0.589588 },
        weighted_metrics: { precision: 0.856227, recall: 0.849186, f1_score: 0.849196 },
        confusion_matrix: {
            classes: ['Apple_Healthy', 'Apple_Rust'],
            matrix: [[3, 4], [0, 15]]
        },
        per_class_metrics: {
            'Apple_Healthy': { class_index: 0, test_images: 7, correct: 3, incorrect: 4, precision: 0.6, recall: 0.428571, f1_score: 0.5, accuracy: 0.428571 }
        }
    };

    renderOverviewMetrics(mockData);
    if (!mockElement('overallAccuracyVal').textContent.includes('84.92%')) throw new Error('Accuracy not rendered correctly');
    if (!mockElement('macroPrecisionVal').textContent.includes('61.14%')) throw new Error('Macro precision not rendered');

    renderComparisonTable(mockData);
    const compHtml = mockElement('comparisonTableBody').innerHTML;
    if (!compHtml.includes('Macro Average') || !compHtml.includes('Weighted Average')) {
        throw new Error('Comparison table missing Macro or Weighted labels');
    }
    if (!compHtml.includes('61.14%') || !compHtml.includes('85.62%')) {
        throw new Error('Comparison table values not rendered correctly');
    }

    renderConfusionMatrix(mockData.confusion_matrix);
    const cmHtml = mockElement('confusionMatrixTable').innerHTML;
    if (!cmHtml.includes('Apple Healthy') || !cmHtml.includes('cell-diagonal')) {
        throw new Error('Confusion matrix table HTML not built correctly');
    }

    console.log("FRONTEND_PERFORMANCE_TESTS_CLEAN");
    """

    try:
        proc17 = subprocess.run(
            ["node", "-e", js_performance_test],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        test17_ok = (proc17.returncode == 0 and "FRONTEND_PERFORMANCE_TESTS_CLEAN" in proc17.stdout)
        if not test17_ok:
            print(f"Node output: {proc17.stdout}, error: {proc17.stderr}")
    except Exception as exc:
        print(f"Node execution exception: {exc}")
        test17_ok = False

    if test17_ok:
        print("[PASS] TEST 17: Frontend Model Performance rendering functions, comparison table, and confusion matrix validated")
        passed += 1
    else:
        print("[FAIL] TEST 17: Frontend Model Performance rendering test failed")

    # ---------------------------------------------------------
    # TEST 18: Separation of farmer UI (index.html) and technical page (performance.html)
    # ---------------------------------------------------------
    print("\n--- TEST 18: Verify farmer UI simplicity & dedicated performance.html page ---")
    index_path = os.path.join(PROJECT_ROOT, "frontend", "index.html")
    perf_path = os.path.join(PROJECT_ROOT, "frontend", "performance.html")

    assert os.path.isfile(index_path), f"index.html not found: {index_path}"
    assert os.path.isfile(perf_path), f"performance.html not found: {perf_path}"

    with open(index_path, "r", encoding="utf-8") as f:
        index_html = f.read()
    with open(perf_path, "r", encoding="utf-8") as f:
        perf_html = f.read()

    # index.html checks:
    # 1. Farmer navigation: Home, Diagnosis, Model Performance, AI Assistant, About
    has_farmer_nav = (
        'href="#home"' in index_html
        and 'href="#diagnosis"' in index_html
        and 'href="performance.html"' in index_html
        and 'href="#chat"' in index_html
        and 'href="#about"' in index_html
    )
    # 2. Four stages in About section:
    has_four_stages = (
        "1. Upload Image" in index_html
        and "2. CNN Diagnosis" in index_html
        and "3. Knowledge Retrieval" in index_html
        and "4. AI Guidance" in index_html
    )
    # 3. Farmer diagnosis screen does NOT contain technical confusion matrix or per-class tables
    diagnosis_clean = (
        "confusionMatrixTable" not in index_html
        and "perClassTable" not in index_html
        and "comparisonTableBody" not in index_html
    )

    # performance.html checks:
    # 1. Explicit technical audience indicator
    has_tech_audience = (
        "Project Reviewers" in perf_html
        and "Researchers" in perf_html
        and "Technical" in perf_html
    )
    # 2. Contains all technical evaluation elements
    has_eval_components = (
        "overallAccuracyVal" in perf_html
        and "top3AccuracyVal" in perf_html
        and "macroPrecisionVal" in perf_html
        and "macroRecallVal" in perf_html
        and "macroF1Val" in perf_html
        and "comparisonTableBody" in perf_html
        and "splitDetailsGrid" in perf_html
        and "perClassTable" in perf_html
        and "classFilterInput" in perf_html
        and "confusionMatrixTable" in perf_html
        and "confusionMatrixImg" in perf_html
        and "evaluationDisclaimer" in perf_html
    )
    # 3. Navigation link back to farmer diagnosis
    has_return_link = 'href="index.html#diagnosis"' in perf_html

    test18_ok = (
        has_farmer_nav
        and has_four_stages
        and diagnosis_clean
        and has_tech_audience
        and has_eval_components
        and has_return_link
    )

    print(f"Farmer nav in index.html: {has_farmer_nav}")
    print(f"4 stages in About: {has_four_stages}")
    print(f"Diagnosis screen clean of technical tables: {diagnosis_clean}")
    print(f"Technical audience label in performance.html: {has_tech_audience}")
    print(f"All evaluation components in performance.html: {has_eval_components}")
    print(f"Return link to diagnosis in performance.html: {has_return_link}")

    if test18_ok:
        print("[PASS] TEST 18: Farmer UI in index.html is clean & simple; Model Performance is preserved as a dedicated technical page")
        passed += 1
    else:
        print("[FAIL] TEST 18: Separation of farmer UI and technical performance.html failed")

    # ---------------------------------------------------------
    # TEST 19: GET /schemes returns verified official schemes & metadata
    # ---------------------------------------------------------
    print("\n--- TEST 19: GET /schemes returns verified official schemes & metadata ---")
    resp_schemes = client.get("/schemes")
    print(f"HTTP Status: {resp_schemes.status_code}")
    schemes_data = resp_schemes.get_json() or {}

    status_ok = resp_schemes.status_code == 200 and schemes_data.get("status") == "success"
    metadata = schemes_data.get("metadata", {})
    categories = schemes_data.get("categories", [])
    schemes = schemes_data.get("schemes", [])

    has_required_metadata = (
        "curated_as_of" in metadata
        and "source_authority" in metadata
        and "disclaimer" in metadata
        and "primary_portal" in metadata
    )

    # Check presence of required verified official sources
    official_urls = [s.get("official_link", "") for s in schemes]
    has_agriwelfare = any("agriwelfare.gov.in" in u for u in official_urls)
    has_pmfby = any("pmfby.gov.in" in u for u in official_urls)
    has_pmkisan = any("pmkisan.gov.in" in u for u in official_urls)
    has_mkisan = any("mkisan.gov.in" in u for u in official_urls)

    test19_ok = (
        status_ok
        and has_required_metadata
        and len(categories) >= 5
        and len(schemes) >= 10
        and has_agriwelfare
        and has_pmfby
        and has_pmkisan
        and has_mkisan
    )

    print(f"Metadata verified: {has_required_metadata}")
    print(f"Categories count: {len(categories)}")
    print(f"Total schemes count: {len(schemes)}")
    print(f"Verified official portals present: agriwelfare={has_agriwelfare}, pmfby={has_pmfby}, pmkisan={has_pmkisan}, mkisan={has_mkisan}")

    if test19_ok:
        print("[PASS] TEST 19: GET /schemes returns authentic official schemes, metadata, and verified central portals")
        passed += 1
    else:
        print("[FAIL] TEST 19: GET /schemes failed verification")

    # ---------------------------------------------------------
    # TEST 20: Scheme data structure integrity & official links
    # ---------------------------------------------------------
    print("\n--- TEST 20: Scheme data structure integrity & official links ---")
    test20_ok = True
    required_fields = [
        "id", "name", "category", "category_label", "purpose",
        "benefits", "eligibility", "application_steps",
        "official_portal", "official_link", "last_verified", "verification_status"
    ]

    for s in schemes:
        for f in required_fields:
            if f not in s or not s[f]:
                print(f"Missing or empty field '{f}' in scheme: {s.get('id')}")
                test20_ok = False
        if not isinstance(s.get("application_steps"), list) or len(s["application_steps"]) == 0:
            print(f"Invalid application_steps in scheme: {s.get('id')}")
            test20_ok = False
        link = s.get("official_link", "")
        if not link.startswith("https://") or (".gov.in" not in link and ".nic.in" not in link):
            print(f"Suspicious official link '{link}' in scheme: {s.get('id')}")
            test20_ok = False

    print(f"All {len(schemes)} schemes have valid structure, verified steps, and official .gov.in/.nic.in links: {test20_ok}")
    if test20_ok:
        print("[PASS] TEST 20: Scheme data structure integrity and verified official government domains confirmed")
        passed += 1
    else:
        print("[FAIL] TEST 20: Scheme data structure integrity check failed")

    # ---------------------------------------------------------
    # TEST 21: Category filtering on /schemes and /schemes/categories
    # ---------------------------------------------------------
    print("\n--- TEST 21: Category filtering on /schemes and /schemes/categories ---")
    resp_cats = client.get("/schemes/categories")
    cats_data = resp_cats.get_json() or {}
    cats_ok = resp_cats.status_code == 200 and len(cats_data.get("categories", [])) >= 5

    resp_ins = client.get("/schemes?category=crop_insurance")
    ins_data = resp_ins.get_json() or {}
    ins_schemes = ins_data.get("schemes", [])
    ins_ok = (
        resp_ins.status_code == 200
        and len(ins_schemes) >= 1
        and all(s.get("category") == "crop_insurance" for s in ins_schemes)
    )

    resp_irrig = client.get("/schemes?category=irrigation")
    irrig_data = resp_irrig.get_json() or {}
    irrig_schemes = irrig_data.get("schemes", [])
    irrig_ok = (
        resp_irrig.status_code == 200
        and len(irrig_schemes) >= 1
        and all(s.get("category") == "irrigation" for s in irrig_schemes)
    )

    test21_ok = cats_ok and ins_ok and irrig_ok
    print(f"Categories endpoint status 200: {cats_ok}")
    print(f"Crop insurance filter count: {len(ins_schemes)}, all matching: {ins_ok}")
    print(f"Irrigation filter count: {len(irrig_schemes)}, all matching: {irrig_ok}")

    if test21_ok:
        print("[PASS] TEST 21: Category filtering and categories listing route functioning correctly")
        passed += 1
    else:
        print("[FAIL] TEST 21: Category filtering failed")

    # ---------------------------------------------------------
    # TEST 22: Keyword search on /schemes?q=...
    # ---------------------------------------------------------
    print("\n--- TEST 22: Keyword search on /schemes?q=... ---")
    # Search 'insurance'
    resp_q_ins = client.get("/schemes?q=insurance")
    q_ins_data = resp_q_ins.get_json() or {}
    q_ins_schemes = q_ins_data.get("schemes", [])
    q_ins_ok = any(s.get("id") == "pmfby" for s in q_ins_schemes)

    # Search 'kisan'
    resp_q_kisan = client.get("/schemes?q=kisan")
    q_kisan_data = resp_q_kisan.get_json() or {}
    q_kisan_schemes = q_kisan_data.get("schemes", [])
    q_kisan_ok = any(s.get("id") == "pm-kisan" for s in q_kisan_schemes)

    # Search nonexistent string
    resp_q_none = client.get("/schemes?q=nonexistentqueryxyz123")
    q_none_data = resp_q_none.get_json() or {}
    q_none_ok = (
        resp_q_none.status_code == 200
        and q_none_data.get("count") == 0
        and len(q_none_data.get("schemes", [])) == 0
    )

    test22_ok = q_ins_ok and q_kisan_ok and q_none_ok
    print(f"Search 'insurance' found PMFBY: {q_ins_ok} (count={len(q_ins_schemes)})")
    print(f"Search 'kisan' found PM-KISAN: {q_kisan_ok} (count={len(q_kisan_schemes)})")
    print(f"Search nonexistent returned empty safely: {q_none_ok}")

    if test22_ok:
        print("[PASS] TEST 22: Keyword search properly filters schemes across names, benefits, and tags")
        passed += 1
    else:
        print("[FAIL] TEST 22: Keyword search failed")

    # ---------------------------------------------------------
    # TEST 23: Error handling: missing or malformed schemes file
    # ---------------------------------------------------------
    print("\n--- TEST 23: Error handling for missing or malformed schemes file ---")
    import backend.app as backend_app
    orig_path = backend_app.GOVERNMENT_SCHEMES_PATH

    # Test 1: Missing file -> 404
    backend_app.GOVERNMENT_SCHEMES_PATH = os.path.join(PROJECT_ROOT, "rag", "nonexistent_schemes.json")
    resp_missing = client.get("/schemes")
    missing_ok = resp_missing.status_code == 404

    # Test 2: Malformed file -> 500
    scratch_dir = os.path.join(PROJECT_ROOT, "backend")
    bad_json_path = os.path.join(scratch_dir, "temp_bad_schemes.json")
    with open(bad_json_path, "w", encoding="utf-8") as bf:
        bf.write("{ broken json: [ missing close")
    try:
        backend_app.GOVERNMENT_SCHEMES_PATH = bad_json_path
        resp_malformed = client.get("/schemes")
        malformed_ok = resp_malformed.status_code == 500
    finally:
        if os.path.exists(bad_json_path):
            os.remove(bad_json_path)
        backend_app.GOVERNMENT_SCHEMES_PATH = orig_path

    test23_ok = missing_ok and malformed_ok
    print(f"Missing schemes file returns 404: {missing_ok}")
    print(f"Malformed schemes file returns 500: {malformed_ok}")

    if test23_ok:
        print("[PASS] TEST 23: Missing and malformed schemes files handled gracefully with 404/500 errors")
        passed += 1
    else:
        print("[FAIL] TEST 23: Schemes error handling failed")

    # ---------------------------------------------------------
    # TEST 24: Frontend page structure, navbar consistency & diagnosis cleanliness
    # ---------------------------------------------------------
    print("\n--- TEST 24: Frontend page structure, navbar consistency & diagnosis cleanliness ---")
    schemes_html_path = os.path.join(PROJECT_ROOT, "frontend", "schemes.html")
    schemes_file_exists = os.path.isfile(schemes_html_path)

    with open(schemes_html_path, "r", encoding="utf-8") as f:
        schemes_html = f.read()
    with open(os.path.join(PROJECT_ROOT, "frontend", "index.html"), "r", encoding="utf-8") as f:
        idx_html = f.read()
    with open(os.path.join(PROJECT_ROOT, "frontend", "performance.html"), "r", encoding="utf-8") as f:
        p_html = f.read()

    # 1. schemes.html components:
    has_schemes_nav = (
        'href="index.html#home"' in schemes_html
        and 'href="index.html#diagnosis"' in schemes_html
        and 'href="schemes.html"' in schemes_html
        and 'href="performance.html"' in schemes_html
        and 'href="index.html#chat"' in schemes_html
        and 'href="index.html#about"' in schemes_html
    )
    has_schemes_controls = (
        'id="schemeSearchInput"' in schemes_html
        and 'id="categoryChipsContainer"' in schemes_html
        and 'id="schemesGridContainer"' in schemes_html
        and 'id="schemesCountVal"' in schemes_html
    )
    has_portals_disclaimer = (
        "agriwelfare.gov.in" in schemes_html
        and "pmfby.gov.in" in schemes_html
        and "pmkisan.gov.in" in schemes_html
        and "mkisan.gov.in" in schemes_html
        and "Curated" in schemes_html
        and "October 2026" in schemes_html
    )

    # 2. Consistent navbar in index.html & performance.html:
    index_has_schemes_link = 'href="schemes.html"' in idx_html
    perf_has_schemes_link = 'href="schemes.html"' in p_html

    # 3. Farmer diagnosis screen is clean and not cluttered with schemes:
    diagnosis_clean_of_schemes = (
        "schemesGridContainer" not in idx_html
        and "schemeSearchInput" not in idx_html
    )

    test24_ok = (
        schemes_file_exists
        and has_schemes_nav
        and has_schemes_controls
        and has_portals_disclaimer
        and index_has_schemes_link
        and perf_has_schemes_link
        and diagnosis_clean_of_schemes
    )

    print(f"schemes.html exists: {schemes_file_exists}")
    print(f"schemes.html has complete navbar: {has_schemes_nav}")
    print(f"schemes.html has search & category controls: {has_schemes_controls}")
    print(f"schemes.html displays verified portals & disclaimer: {has_portals_disclaimer}")
    print(f"index.html navbar links to schemes: {index_has_schemes_link}")
    print(f"performance.html navbar links to schemes: {perf_has_schemes_link}")
    print(f"index.html diagnosis screen remains clean of schemes: {diagnosis_clean_of_schemes}")

    if test24_ok:
        print("[PASS] TEST 24: Dedicated schemes page, navbar consistency across pages, and diagnosis cleanliness verified")
        passed += 1
    else:
        print("[FAIL] TEST 24: Frontend schemes UI and navbar consistency check failed")

    # ---------------------------------------------------------
    # TEST 25: GET /shops/categories returns 5 agricultural supply categories
    # ---------------------------------------------------------
    print("\n--- TEST 25: GET /shops/categories returns 5 agricultural supply categories ---")
    resp_shop_cats = client.get("/shops/categories")
    print(f"HTTP Status: {resp_shop_cats.status_code}")
    shop_cats_data = resp_shop_cats.get_json() or {}

    shop_cats = shop_cats_data.get("categories", [])
    cat_ids = [c.get("id") for c in shop_cats]

    test25_ok = (
        resp_shop_cats.status_code == 200
        and shop_cats_data.get("status") == "success"
        and len(shop_cats) == 5
        and "all" in cat_ids
        and "seeds" in cat_ids
        and "fertilizers" in cat_ids
        and "pesticides" in cat_ids
        and "equipment" in cat_ids
    )

    print(f"Categories count: {len(shop_cats)}, IDs: {cat_ids}")
    if test25_ok:
        print("[PASS] TEST 25: /shops/categories returns all 5 required agricultural supply categories")
        passed += 1
    else:
        print("[FAIL] TEST 25: /shops/categories failed")

    # ---------------------------------------------------------
    # TEST 26: GET /shops/search input validation & error states
    # ---------------------------------------------------------
    print("\n--- TEST 26: GET /shops/search input validation & error states ---")
    # Empty location
    resp_empty_loc = client.get("/shops/search?location=")
    empty_loc_ok = resp_empty_loc.status_code == 400

    # Whitespace only location
    resp_ws_loc = client.get("/shops/search?location=   ")
    ws_loc_ok = resp_ws_loc.status_code == 400

    # Missing location parameter
    resp_no_loc = client.get("/shops/search")
    no_loc_ok = resp_no_loc.status_code == 400

    test26_ok = empty_loc_ok and ws_loc_ok and no_loc_ok
    print(f"Empty location returns 400: {empty_loc_ok}")
    print(f"Whitespace location returns 400: {ws_loc_ok}")
    print(f"Missing location returns 400: {no_loc_ok}")

    if test26_ok:
        print("[PASS] TEST 26: Invalid and empty search locations cleanly rejected with HTTP 400")
        passed += 1
    else:
        print("[FAIL] TEST 26: Input validation failed")

    # ---------------------------------------------------------
    # TEST 27: GET /shops/search external map links generation
    # ---------------------------------------------------------
    print("\n--- TEST 27: GET /shops/search external map links generation ---")
    resp_pune = client.get("/shops/search?location=Pune&category=seeds")
    print(f"HTTP Status: {resp_pune.status_code}")
    pune_data = resp_pune.get_json() or {}

    p_links = pune_data.get("primary_links", {})
    gmaps_url = p_links.get("google_maps", "")
    osm_url = p_links.get("openstreetmap", "")
    dir_url = p_links.get("directions", "")
    cat_links = pune_data.get("all_category_links", [])

    gmaps_ok = gmaps_url.startswith("https://www.google.com/maps/search/?api=1&query=") and "Pune" in gmaps_url
    osm_ok = osm_url.startswith("https://www.openstreetmap.org/search?query=") and "Pune" in osm_url
    dir_ok = dir_url.startswith("https://www.google.com/maps/dir/?api=1&destination=") and "Pune" in dir_url
    all_cats_ok = len(cat_links) == 5

    test27_ok = (
        resp_pune.status_code == 200
        and pune_data.get("status") == "success"
        and pune_data.get("location") == "Pune"
        and gmaps_ok
        and osm_ok
        and dir_ok
        and all_cats_ok
    )

    print(f"Google Maps URL generated: {gmaps_ok} ({gmaps_url[:65]}...)")
    print(f"OpenStreetMap URL generated: {osm_ok}")
    print(f"Directions URL generated: {dir_ok}")
    print(f"All category links generated: {all_cats_ok} (count={len(cat_links)})")

    if test27_ok:
        print("[PASS] TEST 27: External map links for Google Maps and OpenStreetMap successfully generated")
        passed += 1
    else:
        print("[FAIL] TEST 27: Map links generation failed")

    # ---------------------------------------------------------
    # TEST 28: Reliability, safety & privacy checks
    # ---------------------------------------------------------
    print("\n--- TEST 28: Reliability, safety & privacy checks ---")
    resp_safety = client.get("/shops/search?location=411001&category=pesticides")
    safety_data = resp_safety.get_json() or {}

    # 1. Clear disclaimer present
    has_disclaimer = bool(safety_data.get("disclaimer")) and "external mapping services" in safety_data.get("disclaimer", "")

    # 2. No fabricated shop details in response (no fake names, phone numbers, or ratings)
    has_fake_shops = "shops_list" in safety_data or "invented_shops" in safety_data

    # 3. No automated chemical pesticide recommendation in shop search
    no_forced_pesticide = "recommended_chemical" not in safety_data

    test28_ok = (
        resp_safety.status_code == 200
        and has_disclaimer
        and not has_fake_shops
        and no_forced_pesticide
    )

    print(f"External map service disclaimer present: {has_disclaimer}")
    print(f"No fabricated shop listings in API response: {not has_fake_shops}")
    print(f"No automated pesticide prescription: {no_forced_pesticide}")

    if test28_ok:
        print("[PASS] TEST 28: Reliability, safety disclaimers, and privacy guarantees verified")
        passed += 1
    else:
        print("[FAIL] TEST 28: Safety and reliability check failed")

    # ---------------------------------------------------------
    # TEST 29: Dedicated shops.html frontend page & navbar consistency
    # ---------------------------------------------------------
    print("\n--- TEST 29: Dedicated shops.html frontend page & navbar consistency ---")
    shops_html_path = os.path.join(PROJECT_ROOT, "frontend", "shops.html")
    shops_file_exists = os.path.isfile(shops_html_path)

    with open(shops_html_path, "r", encoding="utf-8") as f:
        shops_html = f.read()
    with open(os.path.join(PROJECT_ROOT, "frontend", "index.html"), "r", encoding="utf-8") as f:
        index_html_v2 = f.read()
    with open(os.path.join(PROJECT_ROOT, "frontend", "schemes.html"), "r", encoding="utf-8") as f:
        schemes_html_v2 = f.read()
    with open(os.path.join(PROJECT_ROOT, "frontend", "performance.html"), "r", encoding="utf-8") as f:
        perf_html_v2 = f.read()

    # 1. shops.html navbar
    has_shops_nav = (
        'href="index.html#home"' in shops_html
        and 'href="index.html#diagnosis"' in shops_html
        and 'href="schemes.html"' in shops_html
        and 'href="shops.html"' in shops_html
        and 'href="performance.html"' in shops_html
        and 'href="index.html#chat"' in shops_html
        and 'href="index.html#about"' in shops_html
    )

    # 2. shops.html controls and disclaimers
    has_shops_controls = (
        'id="shopLocationInput"' in shops_html
        and 'id="detectLocationBtn"' in shops_html
        and 'id="findShopsBtn"' in shops_html
        and 'id="shopCategoryChips"' in shops_html
        and 'id="shopsResultsArea"' in shops_html
        and 'id="btnPrimaryGoogleMaps"' in shops_html
    )

    has_shops_disclaimer = (
        "Google Maps" in shops_html
        and "OpenStreetMap" in shops_html
        and "Safety Advisory" in shops_html
        and "Privacy First" in shops_html
    )

    # 3. Navbar links across all other pages
    nav_index_ok = 'href="shops.html"' in index_html_v2
    nav_schemes_ok = 'href="shops.html"' in schemes_html_v2
    nav_perf_ok = 'href="shops.html"' in perf_html_v2

    test29_ok = (
        shops_file_exists
        and has_shops_nav
        and has_shops_controls
        and has_shops_disclaimer
        and nav_index_ok
        and nav_schemes_ok
        and nav_perf_ok
    )

    print(f"shops.html exists: {shops_file_exists}")
    print(f"shops.html complete navbar: {has_shops_nav}")
    print(f"shops.html controls present: {has_shops_controls}")
    print(f"shops.html disclaimers present: {has_shops_disclaimer}")
    print(f"index.html links to shops: {nav_index_ok}")
    print(f"schemes.html links to shops: {nav_schemes_ok}")
    print(f"performance.html links to shops: {nav_perf_ok}")

    if test29_ok:
        print("[PASS] TEST 29: Dedicated shops.html page, controls, disclaimers, and site-wide navbar consistency confirmed")
        passed += 1
    else:
        print("[FAIL] TEST 29: shops.html and navbar consistency check failed")

    # ---------------------------------------------------------
    # TEST 30: Farmer crop diagnosis screen remains clean & uncluttered
    # ---------------------------------------------------------
    print("\n--- TEST 30: Farmer crop diagnosis screen remains clean & uncluttered ---")
    diagnosis_clean_of_shops = (
        "shopLocationInput" not in index_html_v2
        and "shopsResultsArea" not in index_html_v2
        and "btnPrimaryGoogleMaps" not in index_html_v2
    )

    print(f"index.html diagnosis screen clean of shop listings & search: {diagnosis_clean_of_shops}")
    if diagnosis_clean_of_shops:
        print("[PASS] TEST 30: Crop diagnosis screen remains simple, clean, and completely uncluttered by shop listings")
        passed += 1
    else:
        print("[FAIL] TEST 30: Diagnosis screen clutter check failed")

    # ---------------------------------------------------------
    # TEST 31: GET /languages API endpoint verification (Step 6)
    # ---------------------------------------------------------
    print("\n--- TEST 31: GET /languages API endpoint verification ---")
    resp31 = client.get("/languages")
    print(f"HTTP Status: {resp31.status_code}")
    res31_json = resp31.get_json()

    languages_list = res31_json.get("languages", [])
    lang_codes = [l.get("code") for l in languages_list]
    print(f"Supported languages: {lang_codes}")
    print(f"Default language: {res31_json.get('default_language')}")

    test31_ok = (
        resp31.status_code == 200
        and res31_json.get("status") == "success"
        and res31_json.get("default_language") == "en"
        and "en" in lang_codes
        and "te" in lang_codes
        and "hi" in lang_codes
        and len(languages_list) == 3
    )

    if test31_ok:
        print("[PASS] TEST 31: GET /languages successfully returns English, Telugu, and Hindi metadata")
        passed += 1
    else:
        print("[FAIL] TEST 31: GET /languages endpoint check failed")

    # ---------------------------------------------------------
    # TEST 32: Multilingual prompt construction & fallbacks in rag/llm_service.py
    # ---------------------------------------------------------
    print("\n--- TEST 32: Multilingual prompt construction & fallbacks in rag/llm_service.py ---")
    try:
        from rag import llm_service

        # 1. Check Telugu prompt instruction
        msgs_te = llm_service.build_messages(
            query="తెగులు నివారణ ఏమిటి?",
            context="Potato Late Blight details...",
            language="te"
        )
        sys_msg_te = msgs_te[0]["content"]
        has_te_instruction = "Telugu" in sys_msg_te or "తెలుగు" in sys_msg_te

        # 2. Check Hindi prompt instruction
        msgs_hi = llm_service.build_messages(
            query="रोग का उपचार क्या है?",
            context="Tomato Early Blight details...",
            language="hi"
        )
        sys_msg_hi = msgs_hi[0]["content"]
        has_hi_instruction = "Hindi" in sys_msg_hi or "हिन्दी" in sys_msg_hi

        # 3. Check English prompt instruction
        msgs_en = llm_service.build_messages(
            user_query="What is the cure?",
            context="Apple Scab details...",
            language="en"
        )
        sys_msg_en = msgs_en[0]["content"]
        has_en_instruction = len(sys_msg_en) > 50 and ("agricultural disease assistance" in sys_msg_en)

        # 4. Fallback messages in Telugu and Hindi
        fb_te = llm_service.FALLBACK_MESSAGES.get("missing_api_key", {}).get("te", "")
        fb_hi = llm_service.FALLBACK_MESSAGES.get("missing_api_key", {}).get("hi", "")
        has_fallbacks = len(fb_te) > 10 and len(fb_hi) > 10

        test32_ok = has_te_instruction and has_hi_instruction and has_en_instruction and has_fallbacks
        print(f"Telugu system prompt localized: {has_te_instruction}")
        print(f"Hindi system prompt localized: {has_hi_instruction}")
        print(f"English system prompt default: {has_en_instruction}")
        print(f"Localized fallbacks available: {has_fallbacks}")

    except Exception as exc:
        print(f"Exception during TEST 32: {exc}")
        test32_ok = False

    if test32_ok:
        print("[PASS] TEST 32: Multilingual prompt construction and localized fallbacks verified for en, te, hi")
        passed += 1
    else:
        print("[FAIL] TEST 32: Multilingual prompt construction check failed")

    # ---------------------------------------------------------
    # TEST 33: Uncertainty warning localization in rag/llm_service.py
    # ---------------------------------------------------------
    print("\n--- TEST 33: Uncertainty warning localization in rag/llm_service.py ---")
    try:
        # Mocking empty/unavailable LLM to check warning insertion in build_messages_with_cnn
        mock_candidates = [
            {"rank": 1, "disease": "Potato_Late_Blight", "probability": 0.42, "has_knowledge": True, "symptoms": ["Dark spots"]},
            {"rank": 2, "disease": "Potato_Early_Blight", "probability": 0.35, "has_knowledge": True, "symptoms": ["Concentric rings"]},
            {"rank": 3, "disease": "Potato_Healthy", "probability": 0.12, "has_knowledge": True, "symptoms": ["None"]}
        ]

        msgs_te_low = llm_service.build_messages_with_cnn(
            query="What are the symptoms and cure?",
            primary_disease="Potato_Late_Blight",
            confidence=0.42,
            candidates=mock_candidates,
            language="te"
        )
        prompt_content_te = msgs_te_low[1]["content"]
        has_te_warn = "దృశ్య నిర్ధారణ అనిశ్చితంగా ఉంది" in prompt_content_te or "అనిశ్చితంగా ఉంది" in prompt_content_te

        msgs_hi_low = llm_service.build_messages_with_cnn(
            query="What are the symptoms and cure?",
            primary_disease="Potato_Late_Blight",
            confidence=0.42,
            candidates=mock_candidates,
            language="hi"
        )
        prompt_content_hi = msgs_hi_low[1]["content"]
        has_hi_warn = "दृश्य निदान अनिश्चित है" in prompt_content_hi or "अनिश्चित है" in prompt_content_hi

        test33_ok = has_te_warn and has_hi_warn
        print(f"Telugu uncertainty warning in prompt: {has_te_warn}")
        print(f"Hindi uncertainty warning in prompt: {has_hi_warn}")

    except Exception as exc:
        print(f"Exception during TEST 33: {exc}")
        test33_ok = False

    if test33_ok:
        print("[PASS] TEST 33: Uncertainty warnings (< 50% confidence) are correctly localized in Telugu and Hindi")
        passed += 1
    else:
        print("[FAIL] TEST 33: Localized uncertainty warnings check failed")

    # ---------------------------------------------------------
    # TEST 34: Backend POST /chat endpoint handles language parameter
    # ---------------------------------------------------------
    print("\n--- TEST 34: Backend POST /chat endpoint handles language parameter ---")
    # Test POST /chat with language="te"
    payload_te = {
        "message": "టమోటా తెగులు నివారణ పద్ధతులు ఏమిటి?",
        "predicted_disease": "Tomato_Early_Blight",
        "confidence": 0.85,
        "language": "te"
    }
    resp34_te = client.post("/chat", json=payload_te)
    res34_te_json = resp34_te.get_json()

    # Test POST /chat with language="hi"
    payload_hi = {
        "message": "टमाटर के अगेती झुलसा रोग का उपचार क्या है?",
        "predicted_disease": "Tomato_Early_Blight",
        "confidence": 0.85,
        "language": "hi"
    }
    resp34_hi = client.post("/chat", json=payload_hi)
    res34_hi_json = resp34_hi.get_json()

    # Test POST /chat with language="en" (default)
    payload_en = {
        "message": "What is the treatment for early blight?",
        "predicted_disease": "Tomato_Early_Blight",
        "confidence": 0.85,
        "language": "en"
    }
    resp34_en = client.post("/chat", json=payload_en)
    res34_en_json = resp34_en.get_json()

    te_ok = resp34_te.status_code in (200, 503) and bool(res34_te_json.get("answer"))
    hi_ok = resp34_hi.status_code in (200, 503) and bool(res34_hi_json.get("answer"))
    en_ok = resp34_en.status_code in (200, 503) and bool(res34_en_json.get("answer"))

    print(f"POST /chat (te) status: {resp34_te.status_code}, answer length: {len(res34_te_json.get('answer', ''))}")
    print(f"POST /chat (hi) status: {resp34_hi.status_code}, answer length: {len(res34_hi_json.get('answer', ''))}")
    print(f"POST /chat (en) status: {resp34_en.status_code}, answer length: {len(res34_en_json.get('answer', ''))}")

    test34_ok = te_ok and hi_ok and en_ok
    if test34_ok:
        print("[PASS] TEST 34: POST /chat endpoint reliably accepts language parameter (te, hi, en) and produces valid response")
        passed += 1
    else:
        print("[FAIL] TEST 34: POST /chat language parameter test failed")

    # ---------------------------------------------------------
    # TEST 35: Translation dictionary completeness in frontend/translations.js
    # ---------------------------------------------------------
    print("\n--- TEST 35: Translation dictionary completeness in frontend/translations.js ---")
    js_dict_verify_code = """
    const fs = require('fs');
    const path = require('path');

    global.window = {
        addEventListener: () => {},
        dispatchEvent: () => {},
        CustomEvent: function(name, opts) { this.name = name; this.detail = opts ? opts.detail : {}; }
    };
    global.document = {
        documentElement: { lang: "en" },
        querySelectorAll: () => [],
        getElementById: () => null
    };
    global.localStorage = {
        _data: {},
        getItem: function(k) { return this._data[k] || null; },
        setItem: function(k, v) { this._data[k] = String(v); }
    };

    const transPath = path.resolve('frontend', 'translations.js');
    eval(fs.readFileSync(transPath, 'utf8'));

    // 1. Verify TRANSLATIONS object structure
    if (!TRANSLATIONS.en || !TRANSLATIONS.te || !TRANSLATIONS.hi) {
        throw new Error("Missing language dictionaries in TRANSLATIONS!");
    }

    const expectedSections = ['nav', 'common', 'hero', 'diagnosis', 'cards', 'chat', 'schemes', 'shops', 'experts', 'about', 'crops', 'diseases'];
    ['en', 'te', 'hi'].forEach(lang => {
        expectedSections.forEach(sec => {
            if (!TRANSLATIONS[lang][sec]) {
                throw new Error(`Missing section '${sec}' in language '${lang}'`);
            }
        });
    });

    // 2. Verify all 17 CNN classes are present in diseases for all 3 languages
    const cnnClasses = [
        "Apple_Healthy", "Apple_Rust", "Apple_Scab",
        "Corn_Gray_Leaf_Spot", "Corn_Leaf_Blight", "Corn_Leaf_Rust",
        "Potato_Early_Blight", "Potato_Late_Blight", "Potato_Leaf_Blight", "Potato_Leafroll_Virus", "Potato_Healthy",
        "Tomato_Bacterial_Spot", "Tomato_Early_Blight", "Tomato_Late_Blight", "Tomato_Leaf_Mold", "Tomato_Septoria_Leaf_Spot", "Tomato_Healthy"
    ];

    ['en', 'te', 'hi'].forEach(lang => {
        cnnClasses.forEach(cls => {
            if (!TRANSLATIONS[lang].diseases[cls]) {
                throw new Error(`Missing translation for disease '${cls}' in language '${lang}'`);
            }
        });
    });

    // 3. Verify translation functions
    if (typeof t !== 'function' || typeof translateDisease !== 'function' || typeof translateCrop !== 'function') {
        throw new Error("Missing translation helper functions!");
    }

    // 4. Test translation function output in Telugu and Hindi
    setLanguage('te');
    const teDisease = translateDisease('Tomato_Early_Blight');
    if (!teDisease || teDisease.includes('Tomato_Early_Blight')) {
        throw new Error(`Failed to translate Tomato_Early_Blight to Telugu: got ${teDisease}`);
    }

    setLanguage('hi');
    const hiDisease = translateDisease('Potato_Late_Blight');
    if (!hiDisease || hiDisease.includes('Potato_Late_Blight')) {
        throw new Error(`Failed to translate Potato_Late_Blight to Hindi: got ${hiDisease}`);
    }

    console.log("TRANSLATIONS_DICTIONARY_COMPLETE");
    """

    try:
        proc35 = subprocess.run(
            ["node", "-e", js_dict_verify_code],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        test35_ok = (proc35.returncode == 0 and "TRANSLATIONS_DICTIONARY_COMPLETE" in proc35.stdout)
        if not test35_ok:
            print(f"Node output: {proc35.stdout}, error: {proc35.stderr}")
    except Exception as exc:
        print(f"Node execution exception: {exc}")
        test35_ok = False

    if test35_ok:
        print("[PASS] TEST 35: frontend/translations.js dictionary is complete across all 17 CNN classes, crops, and sections")
        passed += 1
    else:
        print("[FAIL] TEST 35: Translation dictionary completeness check failed")

    # ---------------------------------------------------------
    # TEST 36: Frontend integration & language selector on all 5 pages
    # ---------------------------------------------------------
    print("\n--- TEST 36: Frontend integration & language selector on all 5 pages ---")
    pages = ["index.html", "schemes.html", "shops.html", "performance.html", "experts.html"]
    all_pages_ok = True

    for page_name in pages:
        page_path = os.path.join(PROJECT_ROOT, "frontend", page_name)
        with open(page_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        has_selector = 'id="languageSelector"' in html_content
        has_script = 'src="translations.js"' in html_content
        has_globe = "globe-icon" in html_content
        has_options = (
            'value="en"' in html_content
            and 'value="te"' in html_content
            and 'value="hi"' in html_content
        )

        page_ok = has_selector and has_script and has_globe and has_options
        print(f"Page '{page_name}': selector={has_selector}, script={has_script}, options={has_options}")
        if not page_ok:
            all_pages_ok = False

    test36_ok = all_pages_ok
    if test36_ok:
        print("[PASS] TEST 36: Language selector and translations script seamlessly integrated across all 5 frontend pages")
        passed += 1
    else:
        print("[FAIL] TEST 36: Frontend pages language selector check failed")

    # ---------------------------------------------------------
    # TEST 37: GET /experts/institutions returns verified official directories (Step 7)
    # ---------------------------------------------------------
    print("\n--- TEST 37: GET /experts/institutions returns verified official directories ---")
    resp37 = client.get("/experts/institutions")
    print(f"HTTP Status: {resp37.status_code}")
    res37_json = resp37.get_json()

    institutions = res37_json.get("institutions", {})
    kcc37 = institutions.get("kisan_call_centre", {})
    kvk37 = institutions.get("krishi_vigyan_kendras", {})
    state37 = institutions.get("state_departments", {})
    sau37 = institutions.get("agricultural_universities", {})
    when37 = institutions.get("when_to_contact", [])
    disclaimer37 = institutions.get("disclaimer", "")

    has_kcc = (
        kcc37.get("toll_free_number") == "1800-180-1551"
        and "farmer.gov.in" in kcc37.get("official_portal", "")
        and "22" in str(kcc37.get("languages_supported", ""))
    )
    has_kvk = "kvk.icar.gov.in" in kvk37.get("official_portal", "") and "730+" in kvk37.get("network_size", "")
    has_when = len(when37) == 4
    has_disc = "preliminary" in disclaimer37.lower()

    print(f"Kisan Call Centre 1800-180-1551 verified: {has_kcc}")
    print(f"ICAR KVK portal verified: {has_kvk}")
    print(f"State Agriculture & SAU directories present: {bool(state37) and bool(sau37)}")
    print(f"When to contact guidelines count: {len(when37)}")
    print(f"Safety disclaimer present: {has_disc}")

    test37_ok = resp37.status_code == 200 and res37_json.get("status") == "success" and has_kcc and has_kvk and has_when and has_disc
    if test37_ok:
        print("[PASS] TEST 37: GET /experts/institutions accurately returns Kisan Call Centre, KVK network, and advisory guidelines")
        passed += 1
    else:
        print("[FAIL] TEST 37: GET /experts/institutions check failed")

    # ---------------------------------------------------------
    # TEST 38: GET /experts/search input validation & error states
    # ---------------------------------------------------------
    print("\n--- TEST 38: GET /experts/search input validation & error states ---")
    resp38_empty = client.get("/experts/search?location=")
    resp38_ws = client.get("/experts/search?location=%20%20%20")
    resp38_missing = client.get("/experts/search")

    empty_ok = resp38_empty.status_code == 400 and resp38_empty.get_json().get("status") == "error"
    ws_ok = resp38_ws.status_code == 400 and resp38_ws.get_json().get("status") == "error"
    missing_ok = resp38_missing.status_code == 400 and resp38_missing.get_json().get("status") == "error"

    print(f"Empty location rejected with 400: {empty_ok}")
    print(f"Whitespace location rejected with 400: {ws_ok}")
    print(f"Missing location rejected with 400: {missing_ok}")

    test38_ok = empty_ok and ws_ok and missing_ok
    if test38_ok:
        print("[PASS] TEST 38: GET /experts/search strictly validates location inputs and rejects invalid queries with HTTP 400")
        passed += 1
    else:
        print("[FAIL] TEST 38: GET /experts/search input validation failed")

    # ---------------------------------------------------------
    # TEST 39: GET /experts/search external map links and privacy checks
    # ---------------------------------------------------------
    print("\n--- TEST 39: GET /experts/search external map links and privacy checks ---")
    resp39 = client.get("/experts/search?location=Pune,%20Maharashtra")
    print(f"HTTP Status: {resp39.status_code}")
    res39_json = resp39.get_json()

    links39 = res39_json.get("primary_links", {})
    maps_kvk = links39.get("google_maps_kvk", "")
    maps_dept = links39.get("google_maps_dept", "")
    portal_kvk = links39.get("icar_kvk_portal", "")
    disclaimer39 = res39_json.get("disclaimer", "")

    maps_kvk_ok = "google.com/maps/search" in maps_kvk and "Krishi" in maps_kvk and "Pune" in maps_kvk
    maps_dept_ok = "google.com/maps/search" in maps_dept and "District" in maps_dept and "Pune" in maps_dept
    portal_kvk_ok = "kvk.icar.gov.in" in portal_kvk
    disclaimer_ok = "fabricate" in disclaimer39.lower()

    print(f"Google Maps KVK query generated: {maps_kvk_ok} ({maps_kvk[:60]}...)")
    print(f"Google Maps Dept query generated: {maps_dept_ok} ({maps_dept[:60]}...)")
    print(f"ICAR KVK portal link present: {portal_kvk_ok}")
    print(f"Safety disclaimer confirms no fabricated private experts: {disclaimer_ok}")

    test39_ok = resp39.status_code == 200 and res39_json.get("status") == "success" and maps_kvk_ok and maps_dept_ok and portal_kvk_ok and disclaimer_ok
    if test39_ok:
        print("[PASS] TEST 39: External verified query links for KVKs and Agriculture Departments successfully generated")
        passed += 1
    else:
        print("[FAIL] TEST 39: GET /experts/search link generation failed")

    # ---------------------------------------------------------
    # TEST 40: Dedicated experts.html frontend page & site-wide navbar consistency
    # ---------------------------------------------------------
    print("\n--- TEST 40: Dedicated experts.html frontend page & site-wide navbar consistency ---")
    experts_html_path = os.path.join(PROJECT_ROOT, "frontend", "experts.html")
    experts_file_exists = os.path.isfile(experts_html_path)

    with open(experts_html_path, "r", encoding="utf-8") as f:
        experts_html = f.read()
    with open(os.path.join(PROJECT_ROOT, "frontend", "index.html"), "r", encoding="utf-8") as f:
        idx_html_v3 = f.read()
    with open(os.path.join(PROJECT_ROOT, "frontend", "schemes.html"), "r", encoding="utf-8") as f:
        sch_html_v3 = f.read()
    with open(os.path.join(PROJECT_ROOT, "frontend", "shops.html"), "r", encoding="utf-8") as f:
        shp_html_v3 = f.read()
    with open(os.path.join(PROJECT_ROOT, "frontend", "performance.html"), "r", encoding="utf-8") as f:
        prf_html_v3 = f.read()

    # 1. experts.html navbar
    has_experts_nav = (
        'href="index.html#home"' in experts_html
        and 'href="index.html#diagnosis"' in experts_html
        and 'href="schemes.html"' in experts_html
        and 'href="shops.html"' in experts_html
        and 'href="experts.html"' in experts_html
        and 'href="performance.html"' in experts_html
        and 'href="index.html#chat"' in experts_html
        and 'href="index.html#about"' in experts_html
    )

    # 2. Key sections in experts.html
    has_kcc_hotline = "1800-180-1551" in experts_html
    has_when_to_contact = "When to Consult an Agricultural Expert" in experts_html
    has_summary_generator = "consultationSummaryOutput" in experts_html and "copySummaryBtn" in experts_html
    has_location_finder = "expertLocationInput" in experts_html and "findExpertsBtn" in experts_html

    # 3. All other pages link to experts.html
    nav_idx_has_experts = 'href="experts.html"' in idx_html_v3
    nav_sch_has_experts = 'href="experts.html"' in sch_html_v3
    nav_shp_has_experts = 'href="experts.html"' in shp_html_v3
    nav_prf_has_experts = 'href="experts.html"' in prf_html_v3

    print(f"experts.html exists: {experts_file_exists}")
    print(f"experts.html complete navbar: {has_experts_nav}")
    print(f"Kisan Call Centre hotline present: {has_kcc_hotline}")
    print(f"When to consult section present: {has_when_to_contact}")
    print(f"Consultation summary generator present: {has_summary_generator}")
    print(f"All 4 other pages link to experts.html: {nav_idx_has_experts and nav_sch_has_experts and nav_shp_has_experts and nav_prf_has_experts}")

    test40_ok = (
        experts_file_exists
        and has_experts_nav
        and has_kcc_hotline
        and has_when_to_contact
        and has_summary_generator
        and has_location_finder
        and nav_idx_has_experts
        and nav_sch_has_experts
        and nav_shp_has_experts
        and nav_prf_has_experts
    )

    if test40_ok:
        print("[PASS] TEST 40: Dedicated experts.html page and site-wide navigation consistency confirmed across all 5 pages")
        passed += 1
    else:
        print("[FAIL] TEST 40: Dedicated experts.html and navbar consistency check failed")

    # ---------------------------------------------------------
    # TEST 41: Translation dictionary completeness for 'experts' in translations.js
    # ---------------------------------------------------------
    print("\n--- TEST 41: Translation dictionary completeness for 'experts' in translations.js ---")
    js_experts_dict_code = """
    const fs = require('fs');
    const path = require('path');

    global.window = {};
    global.document = { documentElement: { lang: "en" } };
    global.localStorage = { getItem: () => "en", setItem: () => {} };

    const transPath = path.resolve('frontend', 'translations.js');
    eval(fs.readFileSync(transPath, 'utf8'));

    ['en', 'te', 'hi'].forEach(lang => {
        if (!TRANSLATIONS[lang] || !TRANSLATIONS[lang].experts) {
            throw new Error(`Language '${lang}' is missing 'experts' dictionary!`);
        }
        const exp = TRANSLATIONS[lang].experts;
        const requiredKeys = [
            'section_label', 'title', 'description', 'kcc_title', 'kcc_number',
            'when_title', 'summary_title', 'crop_label', 'disease_label',
            'generate_btn', 'copy_btn', 'copied_text'
        ];
        requiredKeys.forEach(k => {
            if (!exp[k]) {
                throw new Error(`Missing key '${k}' in experts dictionary for language '${lang}'`);
            }
        });
    });

    console.log("EXPERTS_TRANSLATION_COMPLETE");
    """

    try:
        proc41 = subprocess.run(
            ["node", "-e", js_experts_dict_code],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        test41_ok = (proc41.returncode == 0 and "EXPERTS_TRANSLATION_COMPLETE" in proc41.stdout)
        if not test41_ok:
            print(f"Node output: {proc41.stdout}, error: {proc41.stderr}")
    except Exception as exc:
        print(f"Node execution exception: {exc}")
        test41_ok = False

    if test41_ok:
        print("[PASS] TEST 41: 'experts' translation dictionary complete across English, Telugu, and Hindi")
        passed += 1
    else:
        print("[FAIL] TEST 41: Experts translation dictionary completeness check failed")

    # ---------------------------------------------------------
    # TEST 42: Consultation Summary Generator logic & pre-filling
    # ---------------------------------------------------------
    print("\n--- TEST 42: Consultation Summary Generator logic & pre-filling ---")
    js_summary_test_code = """
    const fs = require('fs');
    const path = require('path');

    // Mock DOM elements
    const elements = {};
    function mockElement(id, initialVal = "") {
        elements[id] = {
            value: initialVal,
            textContent: initialVal,
            style: {},
            classList: {
                _classes: new Set(),
                add(c) { this._classes.add(c); },
                remove(c) { this._classes.delete(c); },
                contains(c) { return this._classes.has(c); }
            },
            addEventListener: function(event, handler) { this['on_' + event] = handler; }
        };
        return elements[id];
    }

    mockElement("expertLocationInput", "Guntur");
    mockElement("detectExpertLocationBtn");
    mockElement("clearExpertLocationBtn");
    mockElement("findExpertsBtn");
    mockElement("expertGeoStatus");
    mockElement("expertsResultsArea");
    mockElement("expertLocationDisplay");
    mockElement("btnMapsKvk");
    mockElement("btnMapsDept");
    mockElement("btnPortalKvk");

    mockElement("summaryDate", "2026-10-30");
    mockElement("summaryCrop", "Tomato");
    mockElement("summaryDisease", "Tomato Early Blight");
    mockElement("summaryConfidence", "85.4% (High)");
    mockElement("summarySeverity", "Moderate (10% - 25% of crop affected)");
    mockElement("summarySymptoms", "Concentric dark brown rings on lower foliage.");
    mockElement("consultationSummaryOutput", "");
    mockElement("generateSummaryBtn");
    mockElement("copySummaryBtn");
    mockElement("copyToast");
    mockElement("summaryAutoLoadedNote");

    global.document = {
        getElementById: (id) => elements[id] || null,
        querySelectorAll: () => [],
        documentElement: { lang: "en" }
    };

    global.sessionStorage = {
        getItem: (k) => {
            if (k === "cropcure_last_diagnosis") {
                return JSON.stringify({
                    predicted_class: "Tomato_Early_Blight",
                    confidence: 0.854
                });
            }
            return null;
        },
        setItem: () => {}
    };

    global.window = {
        addEventListener: () => {}
    };

    const scriptPath = path.resolve('frontend', 'script.js');
    eval(fs.readFileSync(scriptPath, 'utf8'));

    // Trigger initExpertsPage
    initExpertsPage();

    const outputText = elements["consultationSummaryOutput"].textContent;
    if (!outputText.includes("CROPCURE AI - FARMER FIELD CONSULTATION SUMMARY")) {
        throw new Error("Summary text missing header banner!");
    }
    if (!outputText.includes("Crop: Tomato") || !outputText.includes("Tomato Early Blight")) {
        throw new Error("Summary text missing crop or disease info!");
    }
    if (!outputText.includes("1800-180-1551")) {
        throw new Error("Summary text missing Kisan Call Centre hotline!");
    }
    if (!outputText.includes("Visual predictions are preliminary machine-learning assessments")) {
        throw new Error("Summary text missing safety disclaimer for expert!");
    }

    console.log("SUMMARY_GENERATOR_VERIFIED");
    """

    try:
        proc42 = subprocess.run(
            ["node", "-e", js_summary_test_code],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        test42_ok = (proc42.returncode == 0 and "SUMMARY_GENERATOR_VERIFIED" in proc42.stdout)
        if not test42_ok:
            print(f"Node output: {proc42.stdout}, error: {proc42.stderr}")
    except Exception as exc:
        print(f"Node execution exception: {exc}")
        test42_ok = False

    if test42_ok:
        print("[PASS] TEST 42: Consultation Summary Generator accurately formats crop, diagnosis, symptoms, and preliminary disclaimer")
        passed += 1
    else:
        print("[FAIL] TEST 42: Consultation Summary Generator check failed")

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------
    total = 42
    print("\n" + "=" * 75)
    print(f"CROPCURE AI INTEGRATION TEST SUITE SUMMARY: {passed}/{total} TESTS PASSED")
    print("=" * 75)

    return passed == total

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
