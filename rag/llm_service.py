"""LLM response-generation layer on top of the validated RAG retriever.

Flow:
    user_query -> retrieve() -> context formatting -> grounded prompt
               -> Groq chat completion -> {"success", "answer", "sources"}

Configuration (environment variables, optionally loaded from a ``.env`` file
in the project root; real values must never be committed):

    GROQ_API_KEY   required for the LLM call
    GROQ_MODEL     optional, defaults to DEFAULT_GROQ_MODEL
"""
import os
import pathlib
from typing import Dict, List, Optional

import httpx

from rag.retriever import retrieve, retrieve_for_candidate, get_disease_entry

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# Verified active via GET /openai/v1/models. (llama-3.3-70b-versatile was NOT
# in the active list.) Override with GROQ_MODEL if Groq retires this model.
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
REQUEST_TIMEOUT_SECONDS = 30.0

SYSTEM_PROMPT = (
    "You are an agricultural disease assistance system.\n\n"
    "Answer the user's question using the provided agricultural context.\n\n"
    "Do not invent symptoms, treatments, prevention methods, chemical "
    "recommendations, or other agricultural facts that are not supported by "
    "the retrieved context.\n\n"
    "If the provided context does not contain enough information, clearly "
    "say that the available knowledge base does not contain enough "
    "information to answer reliably.\n\n"
    "Give a clear, practical and easy-to-understand answer. Only include "
    "sections (disease, symptoms, treatment, prevention) that the context "
    "supports.\n\n"
    "Strict rules: every statement must be directly supported by the "
    "retrieved context. Do not add extra tips, timing, weather or "
    "temperature advice, product types, 'key points', or general farming "
    "knowledge from outside the context. Do not move prevention advice into "
    "when the question asks only about symptoms, treatment or prevention, "
    "answer only that part."
)

LANGUAGE_INSTRUCTIONS = {
    "te": (
        "\n\nLANGUAGE INSTRUCTION (TELUGU):\n"
        "You must respond entirely in natural, fluent Telugu (తెలుగు).\n"
        "Translate all symptoms, treatments, prevention measures, and candidate advice grounded strictly in the retrieved agricultural context into Telugu.\n"
        "Keep the crop and disease names clear in Telugu script (you may mention the English term in parentheses if helpful).\n"
        "Do NOT invent facts, remedies, dosages, or advice outside the provided agricultural context."
    ),
    "hi": (
        "\n\nLANGUAGE INSTRUCTION (HINDI):\n"
        "You must respond entirely in natural, fluent Hindi (हिन्दी / देवनागरी).\n"
        "Translate all symptoms, treatments, prevention measures, and candidate advice grounded strictly in the retrieved agricultural context into Hindi.\n"
        "Keep the crop and disease names clear in Hindi script (you may mention the English term in parentheses if helpful).\n"
        "Do NOT invent facts, remedies, dosages, or advice outside the provided agricultural context."
    ),
    "en": ""
}

UNCERTAINTY_WARNINGS = {
    "en": "Visual diagnosis is uncertain ({conf_pct}% < 50.0%). The model identified multiple candidate possibilities. Treat this as provisional guidance and compare candidate symptoms before taking action.",
    "te": "దృశ్య నిర్ధారణ అనిశ్చితంగా ఉంది ({conf_pct}% < 50.0%). మోడల్ బహుళ సంభావ్యతలను గుర్తించింది. దీనిని తాత్కాలిక సూచనగా పరిగణించి, చర్యలు తీసుకునే ముందు అభ్యర్థి లక్షణాలను సరిపోల్చండి.",
    "hi": "दृश्य निदान अनिश्चित है ({conf_pct}% < 50.0%)। मॉडल ने कई संभावित विकल्पों की पहचान की है। इसे अनंतिम मार्गदर्शन मानें और कार्रवाई करने से पहले संभावित लक्षणों की तुलना करें।"
}

FALLBACK_MESSAGES = {
    "empty_query": {
        "en": "Please enter a question.",
        "te": "దయచేసి ఒక ప్రశ్నను నమోదు చేయండి.",
        "hi": "कृपया एक प्रश्न दर्ज करें।"
    },
    "no_documents": {
        "en": "No relevant information was found in the agricultural knowledge base for this question.",
        "te": "ఈ ప్రశ్నకు సంబంధిత సమాచారం వ్యవసాయ డేటాబేస్‌లో కనుగొనబడలేదు.",
        "hi": "इस प्रश्न के लिए कृषि ज्ञानकोष में कोई प्रासंगिक जानकारी नहीं मिली।"
    },
    "missing_api_key": {
        "en": "LLM is not configured: set the GROQ_API_KEY environment variable (see .env.example).",
        "te": "LLM కాన్ఫిగర్ చేయబడలేదు: GROQ_API_KEY ఎన్విరాన్‌మెంట్ వేరియబుల్‌ను సెట్ చేయండి (.env.example చూడండి).",
        "hi": "LLM कॉन्फ़िगर नहीं है: GROQ_API_KEY वातावरण चर सेट करें (.env.example देखें)।"
    }
}


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------
def _load_dotenv() -> None:
    """Minimal .env loader (no extra dependency). Never overrides real env vars."""
    env_path = BASE_DIR / ".env"
    if not env_path.is_file():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def get_api_key() -> Optional[str]:
    """Return the configured Groq key, ignoring empty/placeholder values."""
    _load_dotenv()
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key or key == "your_groq_api_key_here":
        return None
    return key


def get_model_name() -> str:
    _load_dotenv()
    model = os.getenv("GROQ_MODEL", "").strip()
    if not model or model == "your_model_name_here":
        return DEFAULT_GROQ_MODEL
    return model


# ---------------------------------------------------------------------------
# Context / prompt construction
# ---------------------------------------------------------------------------
def format_context(results: List[dict]) -> str:
    """Convert retrieve() results into a readable context block."""
    blocks = []
    for i, res in enumerate(results, start=1):
        d = res["data"]
        symptoms = d.get("symptoms", [])
        if isinstance(symptoms, list):
            symptoms = "; ".join(symptoms)
        blocks.append(
            f"[Record {i}]\n"
            f"Crop: {d.get('crop', '')}\n"
            f"Disease: {d.get('disease', '')}\n"
            f"Symptoms: {symptoms}\n"
            f"Treatment: {d.get('treatment', '')}\n"
            f"Prevention: {d.get('prevention', '')}"
        )
    return "\n\n".join(blocks)


def build_messages(context: str = "", user_query: str = "", language: str = "en", **kwargs) -> List[Dict[str, str]]:
    """Build the chat messages with the retrieved context embedded."""
    query_text = user_query or kwargs.get("query", "")
    lang_inst = LANGUAGE_INSTRUCTIONS.get(language, "")
    user_content = (
        f"Retrieved context:\n\n{context}\n\n"
        f"User question:\n{query_text}"
    )
    return [
        {"role": "system", "content": f"{SYSTEM_PROMPT}{lang_inst}"},
        {"role": "user", "content": user_content},
    ]


def _build_sources(results: List[dict]) -> List[dict]:
    return [
        {
            "crop": r["data"].get("crop", ""),
            "disease": r["data"].get("disease", ""),
            "score": round(float(r["score"]), 4),
        }
        for r in results
    ]


# ---------------------------------------------------------------------------
# Groq call
# ---------------------------------------------------------------------------
class LLMError(Exception):
    """Raised with a user-safe message (never contains the API key)."""


def call_groq(messages: List[Dict[str, str]], api_key: str, model: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 1500,
    }
    if "gpt-oss" in model:
        # Reasoning model: keep reasoning short so content is always returned.
        payload["reasoning_effort"] = "low"
    try:
        resp = httpx.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except httpx.TimeoutException:
        raise LLMError("The LLM request timed out. Please try again.")
    except httpx.HTTPError as exc:
        raise LLMError(f"Could not reach the LLM API ({type(exc).__name__}).")

    if resp.status_code != 200:
        detail = ""
        try:
            detail = resp.json().get("error", {}).get("message", "")
        except ValueError:
            pass
        if resp.status_code in (401, 403):
            raise LLMError("The LLM API rejected the credentials (invalid GROQ_API_KEY).")
        if resp.status_code == 404 or "model" in detail.lower():
            raise LLMError(
                f"The configured model '{model}' is invalid or unavailable. "
                "Check GROQ_MODEL."
            )
        if resp.status_code == 429:
            raise LLMError("The LLM API rate limit was reached. Please retry shortly.")
        raise LLMError(f"The LLM API returned an error (HTTP {resp.status_code}).")

    try:
        text = resp.json()["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise LLMError("The LLM API returned an unexpected response format.")
    if not text or not text.strip():
        raise LLMError("The LLM returned an empty response.")
    return text.strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def answer_query(user_query: str, top_k: int = 3, language: str = "en") -> dict:
    """Return a grounded answer for ``user_query`` plus the retrieved sources.

    Returns ``{"success": bool, "answer": str, "sources": [...]}``; failures
    additionally carry an ``"error"`` string.
    """
    if language not in ("en", "te", "hi"):
        language = "en"

    if not user_query or not str(user_query).strip():
        empty_msg = FALLBACK_MESSAGES["empty_query"].get(language, FALLBACK_MESSAGES["empty_query"]["en"])
        return {
            "success": False,
            "answer": empty_msg,
            "sources": [],
            "error": "empty_query",
        }
    user_query = str(user_query).strip()

    results = retrieve(user_query, top_k=top_k)
    if not results:
        no_doc_msg = FALLBACK_MESSAGES["no_documents"].get(language, FALLBACK_MESSAGES["no_documents"]["en"])
        return {
            "success": False,
            "answer": no_doc_msg,
            "sources": [],
            "error": "no_documents",
        }

    sources = _build_sources(results)
    messages = build_messages(format_context(results), user_query, language=language)

    api_key = get_api_key()
    if not api_key:
        missing_key_msg = FALLBACK_MESSAGES["missing_api_key"].get(language, FALLBACK_MESSAGES["missing_api_key"]["en"])
        return {
            "success": False,
            "answer": missing_key_msg,
            "sources": sources,
            "error": "missing_api_key",
        }

    try:
        answer = call_groq(messages, api_key, get_model_name())
    except LLMError as exc:
        return {
            "success": False,
            "answer": str(exc),
            "sources": sources,
            "error": "llm_error",
        }

    return {"success": True, "answer": answer, "sources": sources}


# ---------------------------------------------------------------------------
# Visual Diagnosis (CNN) + RAG + Groq Grounding
# ---------------------------------------------------------------------------
SYSTEM_PROMPT_WITH_CNN = (
    "You are an agricultural disease assistance system.\n\n"
    "Answer the user's question using the provided agricultural context and visual diagnosis information.\n\n"
    "Visual Diagnosis Rules:\n"
    "- If the CNN confidence is below 0.50 (< 50%), the visual diagnosis is UNCERTAIN:\n"
    "  1. You MUST explicitly state that the visual diagnosis is UNCERTAIN and that visual symptoms alone cannot confirm the specific disease.\n"
    "  2. Present a differential comparison of the top candidate alternatives based ONLY on the retrieved context for each candidate.\n"
    "  3. For each candidate that has retrieved information, discuss its symptoms, prevention, and provisional management options under clearly labeled candidate sections.\n"
    "  4. DO NOT recommend chemical or irreversible treatment as confirmed or definitive when diagnosis is uncertain! Strongly advise the grower to verify key physical symptoms (e.g. lesion shape, color, leaf position) or consult local agricultural experts before applying targeted chemical treatments.\n"
    "  5. If information for any candidate is missing or marked as unavailable, explicitly state that knowledge for that candidate is not available in the agricultural knowledge base.\n"
    "- If the CNN confidence is 0.50 or higher (>= 50%), you may present the predicted disease as the primary visual diagnosis, and provide symptoms, treatment, and prevention strictly grounded in the retrieved context.\n\n"
    "Grounding Rules:\n"
    "- Every statement regarding disease symptoms, causes, treatments, prevention, and chemical or organic advice must be strictly supported by the retrieved context.\n"
    "- Do not invent treatments, pesticides, dosages, or disease facts outside the retrieved context.\n"
    "- If the retrieved context does not contain enough information to answer a question or part of it, clearly state that the available knowledge base does not contain enough information to answer reliably.\n"
    "- Keep the answer practical, clear, and well-structured."
)


def format_multi_candidate_context(candidates: List[dict]) -> str:
    """Format separated, clearly labeled context blocks for each candidate disease."""
    blocks = []
    for cand in candidates:
        rank = cand["rank"]
        name = cand["clean_name"]
        prob = cand.get("probability")
        prob_str = f" ({float(prob) * 100:.1f}%)" if prob is not None else ""
        header = f"=== Candidate {rank}: {name}{prob_str} ==="

        if not cand["has_knowledge"] or not cand["results"]:
            blocks.append(
                f"{header}\n"
                "Knowledge Base Status: No specific agricultural knowledge record found for this disease in the database."
            )
        else:
            cand_records = []
            for r in cand["results"]:
                d = r["data"]
                symptoms = d.get("symptoms", [])
                if isinstance(symptoms, list):
                    symptoms = "; ".join(symptoms)
                cand_records.append(
                    f"Crop: {d.get('crop', '')}\n"
                    f"Disease: {d.get('disease', '')}\n"
                    f"Symptoms: {symptoms}\n"
                    f"Treatment: {d.get('treatment', '')}\n"
                    f"Prevention: {d.get('prevention', '')}"
                )
            blocks.append(f"{header}\n" + "\n\n".join(cand_records))
    return "\n\n".join(blocks)


def build_messages_with_cnn(
    context: str = "",
    user_query: str = "",
    predicted_disease: Optional[str] = None,
    confidence: Optional[float] = None,
    top3: Optional[list] = None,
    language: str = "en",
    **kwargs
) -> List[Dict[str, str]]:
    """Build grounded chat messages combining CNN visual diagnosis and RAG context."""
    query_text = user_query or kwargs.get("query", "")
    pred_disease = predicted_disease or kwargs.get("primary_disease", None)
    cands_list = top3 or kwargs.get("candidates", None)

    diag_lines = []
    clean_disease = ""
    if pred_disease:
        clean_disease = str(pred_disease).replace("_", " ").strip()
        diag_lines.append(f"Predicted Disease: {clean_disease}")

    is_low_conf = False
    if confidence is not None:
        try:
            c_val = float(confidence)
            is_low_conf = c_val < 0.50
            conf_str = f"{c_val * 100:.1f}%"
            if is_low_conf:
                diag_lines.append(f"Confidence: {conf_str} (LOW - Confidence < 50%, Diagnosis is UNCERTAIN)")
            else:
                diag_lines.append(f"Confidence: {conf_str} (HIGH - Confidence >= 50%, Primary Visual Diagnosis)")
        except (ValueError, TypeError):
            pass

    if cands_list and isinstance(cands_list, list):
        candidates = []
        for item in cands_list:
            if isinstance(item, dict):
                c_name = str(item.get("class", item.get("disease", ""))).replace("_", " ").strip()
                p = item.get("probability")
                if p is not None:
                    candidates.append(f"{c_name} ({float(p) * 100:.1f}%)")
                else:
                    candidates.append(c_name)
            else:
                candidates.append(str(item))
        if candidates:
            diag_lines.append(f"Top-3 Candidate Predictions: {', '.join(candidates)}")

    diag_text = "\n".join(diag_lines) if diag_lines else "None provided."

    instruction_note = ""
    if is_low_conf:
        warn_tpl = UNCERTAINTY_WARNINGS.get(language, UNCERTAINTY_WARNINGS["en"])
        conf_pct_str = f"{float(confidence) * 100:.1f}" if confidence is not None else "< 50.0"
        localized_warn = warn_tpl.format(conf_pct=conf_pct_str)
        instruction_note = (
            f"\nIMPORTANT SAFETY INSTRUCTIONS FOR UNCERTAIN DIAGNOSIS:\n"
            f"Localized Uncertainty Notice: {localized_warn}\n"
            "1. State clearly that the visual diagnosis is UNCERTAIN and that visual features alone cannot confirm the disease.\n"
            "2. Present a differential comparison across each candidate alternative using ONLY their respective retrieved context.\n"
            "3. For each candidate with available knowledge, explain its distinguishing symptoms and preventive/sanitation measures under clearly labeled candidate sections.\n"
            "4. DO NOT recommend chemical or irreversible treatment as confirmed! Advise cultural/sanitation measures and recommend physical confirmation before applying chemical treatments.\n"
            "5. If a candidate has no information available in the knowledge base, explicitly inform the user."
        )

    user_content = (
        f"Visual Diagnosis Information:\n{diag_text}{instruction_note}\n\n"
        f"Retrieved Agricultural Knowledge:\n{context}\n\n"
        f"User Question:\n{query_text}"
    )

    lang_inst = LANGUAGE_INSTRUCTIONS.get(language, "")

    return [
        {"role": "system", "content": f"{SYSTEM_PROMPT_WITH_CNN}{lang_inst}"},
        {"role": "user", "content": user_content},
    ]


def answer_query_with_cnn(
    user_query: str,
    predicted_disease: Optional[str] = None,
    confidence: Optional[float] = None,
    top3: Optional[list] = None,
    top_k: int = 3,
    language: str = "en",
) -> dict:
    """Answer user question grounded in RAG context and conditioned on CNN prediction.

    - When confidence < 0.50 (uncertain), retrieves knowledge separately for each candidate in top-3.
    - When confidence >= 0.50 (primary), retrieves knowledge for the primary predicted disease.
    - Applies strict guardrails to prevent confirming treatments under uncertainty.
    """
    if language not in ("en", "te", "hi"):
        language = "en"

    if not user_query or not str(user_query).strip():
        empty_msg = FALLBACK_MESSAGES["empty_query"].get(language, FALLBACK_MESSAGES["empty_query"]["en"])
        return {
            "success": False,
            "answer": empty_msg,
            "sources": [],
            "error": "empty_query",
        }
    user_query = str(user_query).strip()

    is_uncertain = False
    if confidence is not None:
        try:
            is_uncertain = float(confidence) < 0.50
        except (ValueError, TypeError):
            pass

    sources = []
    candidates_retrieved = []

    # Check whether to execute Multi-Candidate RAG (uncertain prediction with top3 candidates)
    if is_uncertain and top3 and isinstance(top3, list) and len(top3) > 0:
        for idx, item in enumerate(top3[:3]):
            if isinstance(item, dict):
                c_class = str(item.get("class", "")).strip()
                c_prob = item.get("probability")
            else:
                c_class = str(item).strip()
                c_prob = None

            c_clean = c_class.replace("_", " ").strip()
            c_results = retrieve_for_candidate(c_class, query=user_query, top_k=2)
            has_info = len(c_results) > 0

            cand_entry = get_disease_entry(c_class)
            cand_info = {
                "rank": idx + 1,
                "class_name": c_class,
                "clean_name": c_clean,
                "probability": c_prob,
                "has_knowledge": has_info,
                "crop": cand_entry.get("crop", "") if cand_entry else "",
                "disease": cand_entry.get("disease", "") if cand_entry else "",
                "symptoms": cand_entry.get("symptoms", []) if cand_entry else [],
                "treatment": cand_entry.get("treatment", "") if cand_entry else "",
                "prevention": cand_entry.get("prevention", "") if cand_entry else "",
                "results": c_results,
            }
            candidates_retrieved.append(cand_info)

            for r in c_results:
                sources.append({
                    "candidate": c_clean,
                    "crop": r["data"].get("crop", ""),
                    "disease": r["data"].get("disease", ""),
                    "score": round(float(r["score"]), 4),
                })

        context = format_multi_candidate_context(candidates_retrieved)
        primary_knowledge = None
    else:
        # Standard Single-Disease Flow (confidence >= 0.50 or top3 not provided)
        clean_disease = ""
        if predicted_disease:
            clean_disease = str(predicted_disease).replace("_", " ").strip()

        if clean_disease:
            search_query = f"{clean_disease} {user_query}".strip()
        else:
            search_query = user_query

        results = retrieve(search_query, top_k=top_k)
        if not results and clean_disease:
            results = retrieve(user_query, top_k=top_k)

        if not results:
            no_doc_msg = FALLBACK_MESSAGES["no_documents"].get(language, FALLBACK_MESSAGES["no_documents"]["en"])
            return {
                "success": False,
                "answer": no_doc_msg,
                "sources": [],
                "error": "no_documents",
            }

        sources = _build_sources(results)
        context = format_context(results)

        primary_entry = get_disease_entry(clean_disease) if clean_disease else (results[0]["data"] if results else None)
        primary_knowledge = None
        if primary_entry:
            primary_knowledge = {
                "crop": primary_entry.get("crop", ""),
                "disease": primary_entry.get("disease", ""),
                "symptoms": primary_entry.get("symptoms", []),
                "treatment": primary_entry.get("treatment", ""),
                "prevention": primary_entry.get("prevention", ""),
            }

    messages = build_messages_with_cnn(
        context=context,
        user_query=user_query,
        predicted_disease=predicted_disease,
        confidence=confidence,
        top3=top3,
        language=language,
    )

    api_key = get_api_key()
    if not api_key:
        missing_key_msg = FALLBACK_MESSAGES["missing_api_key"].get(language, FALLBACK_MESSAGES["missing_api_key"]["en"])
        return {
            "success": False,
            "answer": missing_key_msg,
            "sources": sources,
            "error": "missing_api_key",
        }

    try:
        answer = call_groq(messages, api_key, get_model_name())
    except LLMError as exc:
        return {
            "success": False,
            "answer": str(exc),
            "sources": sources,
            "error": "llm_error",
        }

    warning = None
    if is_uncertain and confidence is not None:
        warning_tpl = UNCERTAINTY_WARNINGS.get(language, UNCERTAINTY_WARNINGS["en"])
        conf_pct = f"{float(confidence) * 100:.1f}"
        warning = warning_tpl.format(conf_pct=conf_pct)

    return {
        "success": True,
        "answer": answer,
        "sources": sources,
        "uncertain": is_uncertain,
        "warning": warning,
        "knowledge": primary_knowledge,
        "candidates": [
            {
                "rank": c["rank"],
                "class_name": c["class_name"],
                "clean_name": c["clean_name"],
                "probability": c["probability"],
                "has_knowledge": c["has_knowledge"],
                "crop": c.get("crop", ""),
                "disease": c.get("disease", ""),
                "symptoms": c.get("symptoms", []),
                "treatment": c.get("treatment", ""),
                "prevention": c.get("prevention", ""),
            }
            for c in candidates_retrieved
        ] if candidates_retrieved else None,
    }
