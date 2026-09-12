"""Evaluation metrics + plots, and a CLI to evaluate one saved model.

Usage:
    python -m src.evaluate \
        --model results/models/svm_mfcc.joblib \
        --test-features data/features/dev.npz \
        --output-prefix results/svm_mfcc_dev
"""
from __future__ import annotations

import argparse
import json

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
    roc_curve,
)

from src.features_io import load_feature_npz

LABEL_NAMES = ["bonafide", "spoof"]


def compute_eer(y_true: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    """Equal Error Rate: threshold where false-accept rate == false-reject rate.

    `scores` must be higher = more likely class 1 (spoof). Returns (eer, threshold).
    """
    fpr, tpr, thresholds = roc_curve(y_true, scores, pos_label=1)
    fnr = 1 - tpr
    idx = int(np.nanargmin(np.abs(fnr - fpr)))
    eer = float((fpr[idx] + fnr[idx]) / 2)
    return eer, float(thresholds[idx])


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_score: np.ndarray) -> dict:
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label=1, zero_division=0
    )
    eer, eer_threshold = compute_eer(y_true, y_score)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    try:
        auc = roc_auc_score(y_true, y_score)
    except ValueError:
        auc = float("nan")  # only one class present in y_true
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_spoof": float(precision),
        "recall_spoof": float(recall),
        "f1_spoof": float(f1),
        "roc_auc": float(auc),
        "eer": eer,
        "eer_threshold": eer_threshold,
        "confusion_matrix": cm.tolist(),
        "n_samples": int(len(y_true)),
    }


def plot_confusion_matrix(cm: np.ndarray, output_path: str, title: str = "Confusion matrix"):
    fig, ax = plt.subplots(figsize=(4, 4))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1], LABEL_NAMES)
    ax.set_yticks([0, 1], LABEL_NAMES)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                     color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_roc_curve(y_true: np.ndarray, y_score: np.ndarray, output_path: str, title: str = "ROC curve"):
    fpr, tpr, _ = roc_curve(y_true, y_score, pos_label=1)
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.plot(fpr, tpr, label="model")
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="chance")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def per_attack_breakdown(y_true, y_pred, attack_type) -> pd.DataFrame:
    """Accuracy per attack/generator type — used for the generalization experiment
    (rubric item 7): shows whether some unseen synthesis methods are much harder."""
    df = pd.DataFrame({"attack_type": attack_type, "correct": (y_true == y_pred)})
    return df.groupby("attack_type")["correct"].agg(["mean", "count"]).rename(
        columns={"mean": "accuracy", "count": "n"}
    ).sort_values("accuracy")


def evaluate_model(model_path: str, test_features_path: str, output_prefix: str) -> dict:
    bundle = joblib.load(model_path)
    scaler, clf, feature_names = bundle["scaler"], bundle["model"], bundle["features"]

    X, y, meta = load_feature_npz(test_features_path, feature_names)
    X_scaled = scaler.transform(X)
    y_pred = clf.predict(X_scaled)
    y_score = clf.predict_proba(X_scaled)[:, 1]  # P(spoof)

    metrics = compute_metrics(y, y_pred, y_score)

    plot_confusion_matrix(np.array(metrics["confusion_matrix"]), f"{output_prefix}_confusion.png")
    plot_roc_curve(y, y_score, f"{output_prefix}_roc.png")

    breakdown = per_attack_breakdown(y, y_pred, meta["attack_type"])
    breakdown.to_csv(f"{output_prefix}_per_attack.csv")

    with open(f"{output_prefix}_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--test-features", required=True)
    ap.add_argument("--output-prefix", required=True)
    args = ap.parse_args()

    metrics = evaluate_model(args.model, args.test_features, args.output_prefix)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
