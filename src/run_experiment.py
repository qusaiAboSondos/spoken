"""CLI: run the full feature/classifier comparison and save a results table.

This is the "good first experiment" from the project brief:
    1. MFCC + SVM
    2. LFCC + SVM
    3. MFCC + Random Forest
    4. MFCC + spectral features combined + SVM

Usage:
    python -m src.run_experiment \
        --train-features data/features/train.npz \
        --test-features data/features/dev.npz \
        --output-dir results/

Each combo's trained model + plots are saved under --output-dir, and a single
comparison table (results/comparison.csv) is written summarizing all of them
side by side for the report's "Comparative Analysis" section.
"""
from __future__ import annotations

import argparse
import os

import joblib
import pandas as pd

from src.evaluate import evaluate_model
from src.train import train_model

DEFAULT_COMBOS = [
    ("mfcc_svm", ["mfcc"], "svm"),
    ("lfcc_svm", ["lfcc"], "svm"),
    ("mfcc_rf", ["mfcc"], "random_forest"),
    ("mfcc_spectral_svm", ["mfcc", "spectral"], "svm"),
    ("mfcc_lfcc_spectral_svm", ["mfcc", "lfcc", "spectral"], "svm"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-features", required=True)
    ap.add_argument("--test-features", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    from src.features_io import load_feature_npz  # local import to keep CLI startup fast

    os.makedirs(os.path.join(args.output_dir, "models"), exist_ok=True)

    rows = []
    for name, feature_names, classifier in DEFAULT_COMBOS:
        print(f"\n=== {name} ({'+'.join(feature_names)} + {classifier}) ===")
        X, y, _ = load_feature_npz(args.train_features, feature_names)
        scaler, clf = train_model(X, y, classifier)

        model_path = os.path.join(args.output_dir, "models", f"{name}.joblib")
        joblib.dump({"scaler": scaler, "model": clf, "features": feature_names}, model_path)

        output_prefix = os.path.join(args.output_dir, name)
        metrics = evaluate_model(model_path, args.test_features, output_prefix)
        metrics.pop("confusion_matrix")  # keep the summary table compact; full CM is in the JSON/PNG
        metrics["experiment"] = name
        metrics["features"] = "+".join(feature_names)
        metrics["classifier"] = classifier
        rows.append(metrics)
        print({k: v for k, v in metrics.items() if k not in ("experiment",)})

    df = pd.DataFrame(rows).set_index("experiment")
    cols = ["features", "classifier", "accuracy", "precision_spoof", "recall_spoof",
            "f1_spoof", "roc_auc", "eer", "n_samples"]
    df = df[cols]
    comparison_path = os.path.join(args.output_dir, "comparison.csv")
    df.to_csv(comparison_path)
    print(f"\nSaved comparison table -> {comparison_path}")
    print(df.to_string())


if __name__ == "__main__":
    main()
