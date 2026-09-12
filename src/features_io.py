"""Load cached feature .npz files (from extract_features.py) and combine
selected feature types into a single matrix."""
from __future__ import annotations

import numpy as np


def load_feature_npz(path: str, feature_names: list[str]):
    """Returns (X, y, meta) where meta has file_id/attack_type/speaker_id arrays.

    Concatenates the requested feature arrays (X_<name>) column-wise, in the
    order given, so e.g. ["mfcc", "spectral"] gives MFCC combined with
    spectral features for the "feature combination" experiment.
    """
    data = np.load(path, allow_pickle=True)
    missing = [name for name in feature_names if f"X_{name}" not in data]
    if missing:
        raise KeyError(
            f"{path} does not contain feature(s) {missing}. "
            f"Available: {[k for k in data.files if k.startswith('X_')]}"
        )
    X = np.concatenate([data[f"X_{name}"] for name in feature_names], axis=1)
    y = data["y"]
    meta = {
        "file_id": data["file_id"],
        "attack_type": data["attack_type"],
        "speaker_id": data["speaker_id"],
    }
    return X, y, meta
