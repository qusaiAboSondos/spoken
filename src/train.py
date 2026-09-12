"""CLI: train a classifier (SVM or Random Forest) on cached features.

Usage:
    python -m src.train \
        --train-features data/features/train.npz \
        --features mfcc lfcc \
        --classifier svm \
        --output results/models/svm_mfcc_lfcc.joblib
"""
from __future__ import annotations

import argparse
import os

import joblib
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.features_io import load_feature_npz

CLASSIFIERS = {
    # CalibratedClassifierCV wraps the SVM to give well-behaved predict_proba
    # scores (needed for ROC-AUC/EER) — plain SVC(probability=True) is deprecated.
    "svm": lambda: CalibratedClassifierCV(
        SVC(kernel="rbf", C=1.0, gamma="scale", class_weight="balanced"), ensemble=False
    ),
    "random_forest": lambda: RandomForestClassifier(
        n_estimators=300, max_depth=None, class_weight="balanced", random_state=0, n_jobs=-1
    ),
}


def train_model(X, y, classifier_name: str):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    clf = CLASSIFIERS[classifier_name]()
    clf.fit(X_scaled, y)
    return scaler, clf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-features", required=True)
    ap.add_argument("--features", nargs="+", default=["mfcc"])
    ap.add_argument("--classifier", choices=list(CLASSIFIERS), default="svm")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    X, y, _meta = load_feature_npz(args.train_features, args.features)
    print(f"Training {args.classifier} on {X.shape[0]} utterances, {X.shape[1]} features "
          f"({'+'.join(args.features)})")

    scaler, clf = train_model(X, y, args.classifier)
    train_acc = clf.score(scaler.transform(X), y)
    print(f"Train accuracy: {train_acc:.4f}")

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    joblib.dump({"scaler": scaler, "model": clf, "features": args.features}, args.output)
    print(f"Saved model -> {args.output}")


if __name__ == "__main__":
    main()
