"""CLI: subsample an ASVspoof protocol file to N utterances per class.

Keeps the original line format untouched (just writes a subset of the
original lines), so the output can be parsed by src.dataset the same way as
the full protocol.

Usage:
    python -m src.subsample_protocol \
        --protocol data/protocols/ASVspoof2019.LA.cm.train.trn.txt \
        --n-per-class 1500 \
        --output data/protocols/train_subset.txt \
        --seed 0
"""
from __future__ import annotations

import argparse
import random

from src.dataset import LABEL_MAP, detect_label_col


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--n-per-class", type=int, required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--label-col", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    with open(args.protocol) as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]

    label_col = args.label_col
    if label_col is None:
        label_col = detect_label_col(lines[0].split())

    by_label: dict[str, list[str]] = {name: [] for name in LABEL_MAP}
    for line in lines:
        tokens = line.split()
        label_name = tokens[label_col].lower()
        if label_name in by_label:
            by_label[label_name].append(line)

    rng = random.Random(args.seed)
    chosen = []
    for label_name, group in by_label.items():
        rng.shuffle(group)
        take = group[: args.n_per_class]
        chosen.extend(take)
        print(f"{label_name}: {len(take)}/{len(group)} kept")

    rng.shuffle(chosen)
    with open(args.output, "w") as f:
        f.write("\n".join(chosen) + "\n")
    print(f"Wrote {len(chosen)} lines -> {args.output}")


if __name__ == "__main__":
    main()
