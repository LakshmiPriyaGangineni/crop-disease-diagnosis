"""
Full CNN test-set evaluation script.

Evaluates every image in data/unified_test/ using the trained CropDiseaseCNN
checkpoint via inference/cnn_inference.py.

Computes:
- Overall Test Accuracy
- Per-class Accuracy, Precision, Recall, F1-score
- Macro and Weighted Precision, Recall, F1-score
- Confusion Matrix (PNG and JSON)
- Classification Report (JSON)
- Error and Discrepancy Analysis (JSON)
"""

import json
import os
import sys
import time

import numpy as np
import torch
import torch.nn.functional as F
from torchvision import datasets
from torch.utils.data import DataLoader

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from inference import cnn_inference as ci  # noqa: E402

TEST_DIR = os.path.join(PROJECT_ROOT, "data", "unified_test")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results", "cnn_evaluation")
BATCH_SIZE = 32


def setup_results_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)


def evaluate_dataset(batch_size=BATCH_SIZE):
    """
    Evaluates every image in data/unified_test using the loaded model and transforms
    from inference.cnn_inference.
    """
    model, classes = ci.load_model()
    model.eval()

    # Load dataset
    test_dataset = datasets.ImageFolder(
        TEST_DIR,
        transform=ci.TRANSFORM
    )

    # Verify class names and ordering
    if test_dataset.classes != classes:
        raise ValueError(
            f"Test dataset classes do not match model checkpoint classes!\n"
            f"Dataset: {test_dataset.classes}\nModel: {classes}"
        )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )

    num_samples = len(test_dataset)
    num_classes = len(classes)

    print(f"Loaded {num_samples} test images across {num_classes} classes.")
    print(f"Device: {ci.DEVICE}")

    y_true = []
    y_pred = []
    y_prob = []
    top3_correct_count = 0

    t0 = time.time()
    with torch.no_grad():
        for i, (images, labels) in enumerate(test_loader):
            images = images.to(ci.DEVICE)
            labels = labels.to(ci.DEVICE)

            logits = model(images)
            probs = F.softmax(logits, dim=1)

            # Top 1 prediction
            _, preds = torch.max(probs, dim=1)

            # Top 3 prediction
            _, top3_preds = torch.topk(probs, k=min(3, num_classes), dim=1)
            for true_lbl, top3 in zip(labels, top3_preds):
                if true_lbl in top3:
                    top3_correct_count += 1

            y_true.extend(labels.cpu().numpy().tolist())
            y_pred.extend(preds.cpu().numpy().tolist())
            y_prob.extend(probs.cpu().numpy().tolist())

            if (i + 1) % 10 == 0 or (i + 1) == len(test_loader):
                processed = min((i + 1) * batch_size, num_samples)
                print(f"  Processed {processed}/{num_samples} images...")

    eval_duration = time.time() - t0
    print(f"Evaluation finished in {eval_duration:.2f}s.")

    return {
        "classes": classes,
        "test_dataset": test_dataset,
        "y_true": y_true,
        "y_pred": y_pred,
        "y_prob": y_prob,
        "top3_correct_count": top3_correct_count,
        "eval_duration_seconds": eval_duration,
    }


def compute_metrics(classes, y_true, y_pred, top3_correct_count):
    """
    Computes confusion matrix, per-class metrics, macro/weighted averages.
    Adheres strictly to standard mathematical formulas.
    """
    num_classes = len(classes)
    total_samples = len(y_true)

    # Confusion matrix: rows = true class, columns = predicted class
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1

    total_correct = int(np.trace(cm))
    total_incorrect = total_samples - total_correct
    overall_accuracy = total_correct / total_samples if total_samples > 0 else 0.0
    top3_accuracy = top3_correct_count / total_samples if total_samples > 0 else 0.0

    per_class_metrics = {}
    macro_precisions = []
    macro_recalls = []
    macro_f1s = []

    for i, cls_name in enumerate(classes):
        support = int(np.sum(cm[i, :]))  # Actual instances of class i
        tp = int(cm[i, i])
        fn = support - tp
        fp = int(np.sum(cm[:, i])) - tp
        tn = total_samples - (tp + fp + fn)

        cls_acc = tp / support if support > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        per_class_metrics[cls_name] = {
            "class_index": i,
            "test_images": support,
            "correct": tp,
            "incorrect": fn,
            "accuracy": round(cls_acc, 6),
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "f1_score": round(f1, 6),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
        }

        macro_precisions.append(precision)
        macro_recalls.append(recall)
        macro_f1s.append(f1)

    macro_precision = float(np.mean(macro_precisions))
    macro_recall = float(np.mean(macro_recalls))
    macro_f1 = float(np.mean(macro_f1s))

    # Weighted averages (weighted by class support)
    supports = [per_class_metrics[c]["test_images"] for c in classes]
    weighted_precision = float(
        np.sum([per_class_metrics[c]["precision"] * s for c, s in zip(classes, supports)]) / total_samples
    )
    weighted_recall = float(
        np.sum([per_class_metrics[c]["recall"] * s for c, s in zip(classes, supports)]) / total_samples
    )
    weighted_f1 = float(
        np.sum([per_class_metrics[c]["f1_score"] * s for c, s in zip(classes, supports)]) / total_samples
    )

    test_metrics = {
        "total_test_images": total_samples,
        "num_classes": num_classes,
        "total_correct": total_correct,
        "total_incorrect": total_incorrect,
        "overall_test_accuracy": round(overall_accuracy, 6),
        "overall_test_accuracy_pct": round(overall_accuracy * 100, 2),
        "top3_accuracy": round(top3_accuracy, 6),
        "top3_accuracy_pct": round(top3_accuracy * 100, 2),
        "macro_avg": {
            "precision": round(macro_precision, 6),
            "recall": round(macro_recall, 6),
            "f1_score": round(macro_f1, 6),
        },
        "weighted_avg": {
            "precision": round(weighted_precision, 6),
            "recall": round(weighted_recall, 6),
            "f1_score": round(weighted_f1, 6),
        },
    }

    classification_report = {}
    for cls_name in classes:
        classification_report[cls_name] = {
            "precision": per_class_metrics[cls_name]["precision"],
            "recall": per_class_metrics[cls_name]["recall"],
            "f1-score": per_class_metrics[cls_name]["f1_score"],
            "support": per_class_metrics[cls_name]["test_images"],
        }
    classification_report["accuracy"] = round(overall_accuracy, 6)
    classification_report["macro avg"] = {
        "precision": round(macro_precision, 6),
        "recall": round(macro_recall, 6),
        "f1-score": round(macro_f1, 6),
        "support": total_samples,
    }
    classification_report["weighted avg"] = {
        "precision": round(weighted_precision, 6),
        "recall": round(weighted_recall, 6),
        "f1-score": round(weighted_f1, 6),
        "support": total_samples,
    }

    return {
        "cm": cm,
        "test_metrics": test_metrics,
        "per_class_metrics": per_class_metrics,
        "classification_report": classification_report,
    }


def plot_confusion_matrix(cm, classes, output_path):
    """
    Plots and saves the confusion matrix using matplotlib without external dependencies.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(14, 12))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=classes,
        yticklabels=classes,
        title="Confusion Matrix - Full CNN Test Set (data/unified_test)",
        ylabel="True Label",
        xlabel="Predicted Label"
    )

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor", fontsize=9)
    plt.setp(ax.get_yticklabels(), fontsize=9)

    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            text = f"{val}" if val > 0 else ""
            ax.text(
                j, i, text,
                ha="center", va="center",
                color="white" if val > thresh else "black",
                fontsize=8,
                fontweight="bold" if i == j and val > 0 else "normal"
            )

    fig.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Confusion matrix plot saved to: {output_path}")


def analyze_errors_and_discrepancy(test_dataset, classes, y_true, y_pred, y_prob, per_class_metrics):
    """
    Analyzes misclassifications and investigates the discrepancy between
    validation accuracy (86.57%) and 1-per-class sample accuracy (52.94%).
    """
    # Identify web-sourced vs PlantVillage dominated classes
    # From class_mapping.json:
    with open(ci.CLASS_MAPPING_PATH, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    web_only_classes = [c for c, src in mapping.items() if list(src.keys()) == ["dataset_6_web_sourced"]]
    plantvillage_classes = [c for c, src in mapping.items() if "dataset_1_plantvillage" in src]
    hybrid_classes = [c for c, src in mapping.items() if c not in web_only_classes and c not in plantvillage_classes]

    # Category performance
    def get_group_stats(class_list):
        total_imgs = sum(per_class_metrics[c]["test_images"] for c in class_list)
        total_cor = sum(per_class_metrics[c]["correct"] for c in class_list)
        acc = total_cor / total_imgs if total_imgs > 0 else 0.0
        return {
            "classes": class_list,
            "test_images": total_imgs,
            "correct": total_cor,
            "accuracy": round(acc, 6),
            "accuracy_pct": round(acc * 100, 2),
        }

    pv_stats = get_group_stats(plantvillage_classes)
    web_stats = get_group_stats(web_only_classes)
    hybrid_stats = get_group_stats(hybrid_classes)

    # Detailed misclassification logs
    misclassified = []
    for idx, (path, label_idx) in enumerate(test_dataset.samples):
        pred_idx = y_pred[idx]
        if pred_idx != label_idx:
            misclassified.append({
                "image_path": os.path.relpath(path, PROJECT_ROOT),
                "true_class": classes[label_idx],
                "predicted_class": classes[pred_idx],
                "confidence": round(float(max(y_prob[idx])), 4),
            })

    analysis = {
        "group_breakdown": {
            "plantvillage_dominated": pv_stats,
            "web_sourced_only": web_stats,
            "hybrid": hybrid_stats,
        },
        "total_misclassifications": len(misclassified),
        "misclassifications_sample": misclassified[:50],  # first 50 misclassifications
    }
    return analysis


def print_per_class_table(classes, per_class_metrics, test_metrics):
    """
    Prints a nicely formatted Markdown table for per-class metrics.
    """
    header = (
        f"| {'Class':<28} | {'Test Images':<11} | {'Correct':<7} | {'Incorrect':<9} | "
        f"{'Accuracy':<8} | {'Precision':<9} | {'Recall':<8} | {'F1-score':<8} |"
    )
    separator = (
        f"|{'-'*30}|{'-'*13}|{'-'*9}|{'-'*11}|{'-'*10}|{'-'*11}|{'-'*10}|{'-'*10}|"
    )
    print("\n" + "=" * 115)
    print("PER-CLASS EVALUATION TABLE (Full Test Set: data/unified_test)")
    print("=" * 115)
    print(header)
    print(separator)

    for c in classes:
        m = per_class_metrics[c]
        row = (
            f"| {c:<28} | {m['test_images']:<11} | {m['correct']:<7} | {m['incorrect']:<9} | "
            f"{m['accuracy']*100:>6.2f}% | {m['precision']:>9.4f} | {m['recall']:>8.4f} | {m['f1_score']:>8.4f} |"
        )
        print(row)

    print(separator)
    tm = test_metrics
    summary_row = (
        f"| {'OVERALL / MACRO AVG':<28} | {tm['total_test_images']:<11} | {tm['total_correct']:<7} | {tm['total_incorrect']:<9} | "
        f"{tm['overall_test_accuracy_pct']:>6.2f}% | {tm['macro_avg']['precision']:>9.4f} | {tm['macro_avg']['recall']:>8.4f} | {tm['macro_avg']['f1_score']:>8.4f} |"
    )
    weighted_row = (
        f"| {'WEIGHTED AVG':<28} | {tm['total_test_images']:<11} | {tm['total_correct']:<7} | {tm['total_incorrect']:<9} | "
        f"{tm['overall_test_accuracy_pct']:>6.2f}% | {tm['weighted_avg']['precision']:>9.4f} | {tm['weighted_avg']['recall']:>8.4f} | {tm['weighted_avg']['f1_score']:>8.4f} |"
    )
    print(summary_row)
    print(weighted_row)
    print("=" * 115 + "\n")


def run_evaluation():
    setup_results_dir()

    print("=" * 70)
    print("STARTING FULL CNN TEST-SET EVALUATION")
    print(f"Test Directory: {TEST_DIR}")
    print(f"Results Directory: {RESULTS_DIR}")
    print("=" * 70)

    # 1. Run inference on full test dataset
    eval_res = evaluate_dataset()
    classes = eval_res["classes"]
    y_true = eval_res["y_true"]
    y_pred = eval_res["y_pred"]
    y_prob = eval_res["y_prob"]
    top3_correct = eval_res["top3_correct_count"]
    test_dataset = eval_res["test_dataset"]

    # 2. Compute metrics
    metrics = compute_metrics(classes, y_true, y_pred, top3_correct)
    cm = metrics["cm"]
    test_metrics = metrics["test_metrics"]
    per_class_metrics = metrics["per_class_metrics"]
    classification_report = metrics["classification_report"]

    # 3. Print per-class table
    print_per_class_table(classes, per_class_metrics, test_metrics)

    # 4. Save results
    metrics_path = os.path.join(RESULTS_DIR, "test_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(test_metrics, f, indent=4)
    print(f"Saved: {metrics_path}")

    class_report_path = os.path.join(RESULTS_DIR, "classification_report.json")
    with open(class_report_path, "w", encoding="utf-8") as f:
        json.dump(classification_report, f, indent=4)
    print(f"Saved: {class_report_path}")

    per_class_path = os.path.join(RESULTS_DIR, "per_class_metrics.json")
    with open(per_class_path, "w", encoding="utf-8") as f:
        json.dump(per_class_metrics, f, indent=4)
    print(f"Saved: {per_class_path}")

    cm_data_path = os.path.join(RESULTS_DIR, "confusion_matrix.json")
    with open(cm_data_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "classes": classes,
                "matrix": cm.tolist()
            },
            f, indent=4
        )
    print(f"Saved: {cm_data_path}")

    # Plot confusion matrix
    cm_plot_path = os.path.join(RESULTS_DIR, "confusion_matrix.png")
    plot_confusion_matrix(cm, classes, cm_plot_path)

    # Error analysis and discrepancy investigation
    analysis = analyze_errors_and_discrepancy(test_dataset, classes, y_true, y_pred, y_prob, per_class_metrics)
    discrepancy_path = os.path.join(RESULTS_DIR, "discrepancy_analysis.json")
    with open(discrepancy_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=4)
    print(f"Saved: {discrepancy_path}")

    print("\nEVALUATION COMPLETE.")
    return test_metrics, per_class_metrics, analysis


if __name__ == "__main__":
    run_evaluation()
