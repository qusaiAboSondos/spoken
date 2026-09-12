"""CLI: extract and cache features for every utterance in a protocol file.

Usage:
    python -m src.extract_features \
        --protocol data/protocols/train_subset.txt \
        --audio-dir data/raw/ASVspoof2019/LA/ASVspoof2019_LA_train/flac \
        --features mfcc lfcc spectral \
        --output data/features/train.npz

Output npz contains, for every requested feature name `f`: array `X_<f>`
(n_utterances, dim_f), plus `y` (labels), `file_id`, `attack_type`,
`speaker_id`. Caching per-feature-type like this lets run_experiment.py try
different feature combinations without re-running the (slow) extraction.
"""
from __future__ import annotations

import argparse
import os

import numpy as np
from tqdm import tqdm

from src.dataset import parse_protocol, resolve_utterances
from src.features import extract_features, load_audio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--audio-dir", required=True)
    ap.add_argument("--features", nargs="+", default=["mfcc", "lfcc", "spectral"])
    ap.add_argument("--output", required=True)
    ap.add_argument("--file-id-col", type=int, default=1)
    ap.add_argument("--attack-col", type=int, default=3)
    args = ap.parse_args()

    df = parse_protocol(args.protocol, file_id_col=args.file_id_col, attack_col=args.attack_col)
    utterances = resolve_utterances(df, args.audio_dir)
    if not utterances:
        raise SystemExit("No audio files resolved — check --audio-dir and the protocol file.")

    per_feature: dict[str, list[np.ndarray]] = {name: [] for name in args.features}
    labels, file_ids, attack_types, speaker_ids = [], [], [], []
    failed = 0

    for utt in tqdm(utterances, desc="extracting features"):
        try:
            y = load_audio(utt.path)
            feats = extract_features(y, sr=16000, feature_names=args.features)
        except Exception as e:  # corrupt/short file — skip, don't crash the whole run
            failed += 1
            print(f"[extract_features] skipping {utt.file_id}: {e}")
            continue
        for name, vec in feats.items():
            per_feature[name].append(vec)
        labels.append(utt.label)
        file_ids.append(utt.file_id)
        attack_types.append(utt.attack_type)
        speaker_ids.append(utt.speaker_id)

    if failed:
        print(f"[extract_features] {failed} files failed and were skipped")

    save_dict = {f"X_{name}": np.stack(vecs) for name, vecs in per_feature.items()}
    save_dict["y"] = np.array(labels)
    save_dict["file_id"] = np.array(file_ids)
    save_dict["attack_type"] = np.array(attack_types)
    save_dict["speaker_id"] = np.array(speaker_ids)

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    np.savez_compressed(args.output, **save_dict)
    print(f"Saved {len(labels)} utterances -> {args.output}")
    for name, vecs in per_feature.items():
        print(f"  {name}: dim={vecs[0].shape[0]}")


if __name__ == "__main__":
    main()
