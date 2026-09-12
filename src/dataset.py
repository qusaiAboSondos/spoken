"""ASVspoof protocol parsing and audio file lookup.

ASVspoof protocol files are whitespace-separated text files with one line per
utterance. The exact column layout differs slightly between ASVspoof2019 and
ASVspoof2021 (2021 has a couple of extra columns), so instead of hard-coding
positions we auto-detect the label column (the one containing the literal
tokens "bonafide"/"spoof") and let the file-id / attack-type columns be
overridden if needed.

Typical ASVspoof2019 LA line:
    LA_0079 LA_T_1138215 - - bonafide
    LA_0079 LA_T_1271820 - A01 spoof
    (speaker_id, file_id, codec placeholder, attack_type, label)
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import pandas as pd

LABEL_MAP = {"bonafide": 0, "spoof": 1}
LABEL_NAMES = {0: "bonafide (real)", 1: "spoof (AI-generated)"}


def detect_label_col(tokens: list[str]) -> int:
    for i, tok in enumerate(tokens):
        if tok.lower() in LABEL_MAP:
            return i
    raise ValueError(f"Could not find a bonafide/spoof label token in: {tokens}")


def parse_protocol(
    protocol_path: str,
    file_id_col: int = 1,
    attack_col: int | None = 3,
    label_col: int | None = None,
) -> pd.DataFrame:
    """Parse an ASVspoof protocol file into a DataFrame with columns:
    [speaker_id, file_id, attack_type, label, label_name].

    file_id_col: column index of the utterance file id (no extension).
    attack_col: column index of the attack/system id ('-' for bonafide).
                Set to None if the protocol doesn't have this column.
    label_col: column index of the bonafide/spoof key. Auto-detected from the
               first non-empty line if not given.
    """
    rows = []
    with open(protocol_path, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    if not lines:
        raise ValueError(f"Protocol file is empty: {protocol_path}")

    if label_col is None:
        label_col = detect_label_col(lines[0].split())

    for line in lines:
        tokens = line.split()
        label_name = tokens[label_col].lower()
        if label_name not in LABEL_MAP:
            # skip malformed lines rather than crash on a whole large file
            continue
        speaker_id = tokens[0]
        file_id = tokens[file_id_col]
        attack_type = tokens[attack_col] if attack_col is not None else "-"
        rows.append(
            {
                "speaker_id": speaker_id,
                "file_id": file_id,
                "attack_type": attack_type,
                "label": LABEL_MAP[label_name],
                "label_name": label_name,
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError(f"No valid bonafide/spoof rows parsed from {protocol_path}")
    return df


def build_audio_index(audio_dir: str, extensions=(".flac", ".wav")) -> dict[str, str]:
    """Walk audio_dir once and map file_id (filename without extension) -> full path.

    Building this index once is much faster than searching the directory tree
    per utterance, which matters once protocols have thousands of entries.
    """
    index: dict[str, str] = {}
    for root, _dirs, files in os.walk(audio_dir):
        for fname in files:
            stem, ext = os.path.splitext(fname)
            if ext.lower() in extensions:
                index[stem] = os.path.join(root, fname)
    return index


@dataclass
class Utterance:
    file_id: str
    path: str
    label: int
    label_name: str
    attack_type: str
    speaker_id: str


def resolve_utterances(df: pd.DataFrame, audio_dir: str) -> list[Utterance]:
    """Join a parsed protocol DataFrame with actual audio file paths.

    Rows whose audio file cannot be found are silently skipped (this is
    expected when working with a subsampled protocol against a partially
    downloaded archive) and the count is printed so it doesn't go unnoticed.
    """
    index = build_audio_index(audio_dir)
    utterances = []
    missing = 0
    for row in df.itertuples(index=False):
        path = index.get(row.file_id)
        if path is None:
            missing += 1
            continue
        utterances.append(
            Utterance(
                file_id=row.file_id,
                path=path,
                label=row.label,
                label_name=row.label_name,
                attack_type=row.attack_type,
                speaker_id=row.speaker_id,
            )
        )
    if missing:
        print(f"[dataset] {missing}/{len(df)} utterances not found under {audio_dir} (skipped)")
    return utterances
