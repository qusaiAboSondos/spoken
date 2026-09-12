"""CLI: generate small synthetic audio + a matching protocol file.

This does NOT stand in for the real dataset — it exists purely so the rest of
the pipeline (feature extraction -> training -> evaluation) can be exercised
and unit-tested in environments without access to the real ASVspoof hosts.
"real" (bonafide) utterances are voiced-like signals built from a few
harmonics with natural jitter; "spoof" ones reuse the same harmonics but add
the kind of artifacts classical vocoders/TTS systems tend to leave behind
(regular phase resets, a clean high-frequency tone) so a classifier trained
on classical spectral features has *something* real to separate them by.

Usage:
    python -m src.make_dummy_data --output-dir data/raw/dummy --n-per-class 20
"""
from __future__ import annotations

import argparse
import os

import numpy as np
import soundfile as sf

SR = 16000
DURATION = 2.0


def make_bonafide(rng: np.random.Generator, f0: float) -> np.ndarray:
    t = np.arange(int(SR * DURATION)) / SR
    y = np.zeros_like(t)
    for h in range(1, 6):
        jitter = 1.0 + rng.normal(0, 0.004)  # natural pitch jitter
        y += (1.0 / h) * np.sin(2 * np.pi * f0 * h * jitter * t + rng.uniform(0, 2 * np.pi))
    envelope = 0.5 * (1 + np.sin(2 * np.pi * 2.0 * t + rng.uniform(0, 2 * np.pi)))
    y = y * (0.4 + 0.6 * envelope)
    y += rng.normal(0, 0.01, size=y.shape)  # mic/room noise
    return (y / np.max(np.abs(y) + 1e-9)).astype(np.float32)


def make_spoof(rng: np.random.Generator, f0: float) -> np.ndarray:
    t = np.arange(int(SR * DURATION)) / SR
    y = np.zeros_like(t)
    for h in range(1, 6):
        y += (1.0 / h) * np.sin(2 * np.pi * f0 * h * t)  # no jitter: too "clean"
    # vocoder-like high-frequency buzz artifact
    y += 0.05 * np.sin(2 * np.pi * 6000 * t)
    envelope = 0.5 * (1 + np.sin(2 * np.pi * 2.0 * t))
    y = y * (0.4 + 0.6 * envelope)
    y += rng.normal(0, 0.002, size=y.shape)  # much cleaner noise floor
    return (y / np.max(np.abs(y) + 1e-9)).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--n-per-class", type=int, default=20)
    ap.add_argument("--protocol-out", default="data/protocols/dummy_protocol.txt")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    protocol_out = args.protocol_out
    os.makedirs(os.path.dirname(protocol_out), exist_ok=True)

    rng = np.random.default_rng(args.seed)
    lines = []
    for i in range(args.n_per_class):
        f0 = rng.uniform(90, 220)  # rough human pitch range

        bona_id = f"DUMMY_bonafide_{i:04d}"
        y = make_bonafide(rng, f0)
        sf.write(os.path.join(args.output_dir, bona_id + ".wav"), y, SR)
        lines.append(f"SPK{i:04d} {bona_id} - - bonafide")

        spoof_id = f"DUMMY_spoof_{i:04d}"
        y = make_spoof(rng, f0)
        sf.write(os.path.join(args.output_dir, spoof_id + ".wav"), y, SR)
        lines.append(f"SPK{i:04d} {spoof_id} - A00 spoof")

    with open(protocol_out, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {2 * args.n_per_class} audio files -> {args.output_dir}")
    print(f"Wrote protocol -> {protocol_out}")


if __name__ == "__main__":
    main()
