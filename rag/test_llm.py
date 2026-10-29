"""Standalone test for the RAG -> LLM pipeline (rag/llm_service.py).

Run from the project root:  python rag/test_llm.py

Without GROQ_API_KEY the real LLM call is skipped (never faked); retrieval,
context formatting, prompt construction and error handling are still tested.
The API key is never printed.
"""
import os
import pathlib
import sys

# LLM output contains non-ASCII characters; avoid cp1252 console crashes.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

project_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

import httpx

from rag import llm_service
from rag.llm_service import (
    answer_query,
    build_messages,
    call_groq,
    format_context,
    get_api_key,
    LLMError,
)
from rag.retriever import retrieve

# (query, expected disease in retrieved sources or None)
TESTS = [
    ("What are the symptoms and treatment for tomato early blight?", "Tomato Early Blight"),
    ("What are the symptoms of tomato early blight?", "Tomato Early Blight"),
    ("How can I treat tomato early blight?", "Tomato Early Blight"),
    ("How can I prevent potato late blight?", "Potato Late Blight"),
    ("What are the symptoms of tomato bacterial spot?", "Tomato Bacterial Spot"),
    ("How can I prevent crop diseases?", None),
    ("Tell me about a disease that is not present in the knowledge base.", None),
]

TOP_K = 3

# Terms that commonly appear when an LLM adds outside agronomy knowledge.
# Flagged only if present in the answer but absent from the retrieved context.
UNSUPPORTED_WATCHLIST = [
    "insecticide", "biological", "resistant", "rotat", "volunteer", "weed",
    "certified", "temperature", "cool", "warm", "spray", "interval",
    "copper", "neem", "organic", "clean tools", "as soon as",
]


def ungrounded_terms(answer, results):
    ctx = format_context(results).lower()
    ans = answer.lower()
    return [t for t in UNSUPPORTED_WATCHLIST if t in ans and t not in ctx]


def check_pipeline(query, expected):
    """Retrieval + context + prompt checks (no network). Returns (ok, results, notes)."""
    notes = []
    results = retrieve(query, top_k=TOP_K)
    ok = bool(results)
    if not results:
        notes.append("no documents retrieved")
        return False, results, notes

    if expected:
        top = results[0]["data"]["disease"]
        if top != expected:
            ok = False
            notes.append(f"expected rank-1 '{expected}', got '{top}'")

    context = format_context(results)
    messages = build_messages(context, query)
    user_msg = messages[1]["content"]
    if messages[0]["role"] != "system" or messages[1]["role"] != "user":
        ok = False
        notes.append("unexpected message roles")
    for r in results:
        if r["data"]["disease"] not in user_msg:
            ok = False
            notes.append(f"context missing {r['data']['disease']}")
    if query not in user_msg:
        ok = False
        notes.append("query missing from prompt")
    return ok, results, notes


def run_error_handling_tests():
    """Offline error-handling checks (HTTP is mocked where noted)."""
    print("\n" + "=" * 70)
    print("ERROR HANDLING TESTS (HTTP mocked where noted)")
    print("=" * 70)
    outcomes = []

    def record(name, cond):
        outcomes.append(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    # Empty query
    r = answer_query("   ")
    record("empty query -> success False, error=empty_query",
           r["success"] is False and r.get("error") == "empty_query")

    # Missing API key
    saved_key = os.environ.pop("GROQ_API_KEY", None)
    saved_loader = llm_service._load_dotenv
    llm_service._load_dotenv = lambda: None  # ignore any local .env for this check
    try:
        r = answer_query("What are the symptoms of tomato early blight?")
        record("missing key -> clear config error, sources still returned",
               r["success"] is False and r.get("error") == "missing_api_key"
               and len(r["sources"]) > 0)
    finally:
        llm_service._load_dotenv = saved_loader
        if saved_key is not None:
            os.environ["GROQ_API_KEY"] = saved_key

    # Mocked HTTP failures
    real_post = httpx.post

    class FakeResp:
        def __init__(self, status, body):
            self.status_code = status
            self._body = body

        def json(self):
            if self._body is None:
                raise ValueError("no json")
            return self._body

    def expect_llm_error(label, fake, needle):
        httpx.post = fake
        try:
            call_groq([{"role": "user", "content": "x"}], "dummy-key", "dummy-model")
            record(label, False)
        except LLMError as exc:
            msg = str(exc)
            record(label, needle in msg and "dummy-key" not in msg)
        finally:
            httpx.post = real_post

    def raise_timeout(*a, **k):
        raise httpx.ReadTimeout("timeout")

    expect_llm_error("[mock] timeout handled", raise_timeout, "timed out")
    expect_llm_error("[mock] 401 invalid key handled",
                     lambda *a, **k: FakeResp(401, {"error": {"message": "bad"}}), "credentials")
    expect_llm_error("[mock] 404 invalid model handled",
                     lambda *a, **k: FakeResp(404, {"error": {"message": "model not found"}}), "invalid or unavailable")
    expect_llm_error("[mock] 500 API failure handled",
                     lambda *a, **k: FakeResp(500, None), "HTTP 500")
    expect_llm_error("[mock] empty LLM response handled",
                     lambda *a, **k: FakeResp(200, {"choices": [{"message": {"content": "  "}}]}), "empty")

    return all(outcomes)


def main():
    api_key_configured = get_api_key() is not None
    if not api_key_configured:
        print("LLM API TEST SKIPPED — GROQ_API_KEY NOT CONFIGURED")
        print("(retrieval, context formatting, prompt construction and error "
              "handling are still tested below)\n")

    all_ok = True
    for query, expected in TESTS:
        print("=" * 70)
        print("QUERY:")
        print(query)

        ok, results, notes = check_pipeline(query, expected)

        print("\nRETRIEVED SOURCES:")
        for r in results:
            print(f"  - {r['data']['crop']} | {r['data']['disease']} | score={r['score']:.4f}")

        if api_key_configured:
            res = answer_query(query, top_k=TOP_K)
            print("\nLLM RESPONSE:")
            print(res["answer"])
            if not res["success"]:
                ok = False
                notes.append(f"LLM call failed: {res.get('error')}")
            else:
                flagged = ungrounded_terms(res["answer"], results)
                if flagged:
                    ok = False
                    notes.append("possible ungrounded terms: " + ", ".join(flagged))
            status = "PASS" if ok else "FAIL"
        else:
            print("\nLLM RESPONSE:")
            print("(not generated — LLM API TEST SKIPPED, GROQ_API_KEY NOT CONFIGURED)")
            status = ("PASS (retrieval/context/prompt only; LLM call NOT tested)"
                      if ok else "FAIL")

        if notes:
            print("\nNOTES: " + "; ".join(notes))
        print("\nSTATUS:")
        print(status)
        all_ok = all_ok and ok

    errors_ok = run_error_handling_tests()

    print("\n" + "=" * 70)
    print(f"Pipeline checks: {'PASS' if all_ok else 'FAIL'}")
    print(f"Error handling : {'PASS' if errors_ok else 'FAIL'}")
    if api_key_configured:
        print("Real LLM calls : executed (see per-query STATUS)")
    else:
        print("Real LLM calls : NOT EXECUTED — GROQ_API_KEY NOT CONFIGURED")
    return 0 if (all_ok and errors_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
