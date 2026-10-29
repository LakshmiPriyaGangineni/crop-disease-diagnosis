import sys
import pathlib

# Ensure project root is in PYTHONPATH
project_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from rag.retriever import retrieve

if __name__ == "__main__":
    demo_queries = [
        "What are the symptoms of tomato early blight?",
        "How can I prevent potato late blight?",
        "What treatment is recommended for bacterial spot?",
    ]
    for q in demo_queries:
        print("\nQuery:", q)
        results = retrieve(q, top_k=2)
        for i, res in enumerate(results, start=1):
            print(f"Result {i}: Score {res['score']:.4f}, Crop {res['data']['crop']}, Disease {res['data']['disease']}")
