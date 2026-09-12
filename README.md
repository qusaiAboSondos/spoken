# Spoken — AI-Generated Speech (Deepfake) Detection

Course project for Spoken Language Processing — Summer 2026 (Birzeit University).
Goal: build a classifier that tells apart **bona fide (real human) speech** from
**AI-generated / deepfake speech** using classical speech features (MFCC, LFCC,
spectral/time-domain features) + classical ML classifiers (SVM, Random Forest).

## Plan (1-week timeline)

| Day | Task |
|---|---|
| 1 | Repo scaffold (done), download a manageable subset of ASVspoof2019 LA (train/dev) + ASVspoof2021 DF (eval) |
| 2 | Feature extraction pipeline (MFCC, LFCC, spectral/time-domain) + caching |
| 3 | Train SVM / Random Forest on MFCC and LFCC separately |
| 4 | Evaluation: accuracy/precision/recall/F1/confusion matrix/ROC-AUC/EER + feature combination experiment |
| 5 | Generalization experiment (train on seen attacks, test on unseen attacks / 2021 DF) |
| 6 | Write IEEE report, figures, tables |
| 7 | Buffer + presentation/demo prep |

## Dataset

We use the **official ASVspoof protocol**, which is the standard, leakage-free way
to do this task:

- **Train / Dev**: ASVspoof **2019 LA** (`train` and `dev` partitions). This is
  the standard training data for deepfake/spoof detection models — it's much
  smaller than 2021 DF and already speaker-disjoint across splits, so there is
  no data leakage.
- **Test (generalization)**: ASVspoof **2021 DF** `eval` partition (or a subset
  of it). This set uses different/unseen TTS & voice-conversion systems than
  2019 LA, so training on 2019 LA and testing on 2021 DF is exactly the
  "unseen generalization" experiment the rubric asks for (item 7).

This mirrors how the official ASVspoof challenge itself is set up, and it's the
most defensible choice for the "Dataset & Experimental Design" rubric item.

See `data/README.md` for exact download commands (next step).

## Project layout

```
src/
  features.py        feature extraction: MFCC, LFCC, spectral, time-domain
  dataset.py          ASVspoof protocol parsing + audio loading
  extract_features.py CLI: precompute & cache features for a protocol split
  train.py             CLI: train SVM / RandomForest on cached features
  evaluate.py          metrics: accuracy, precision, recall, F1, confusion
                        matrix, ROC-AUC, EER + plotting helpers
  run_experiment.py    CLI: end-to-end experiment runner
data/
  protocols/           ASVspoof protocol .txt files (small, committed)
  raw/                 downloaded audio (gitignored, not committed)
  features/            cached extracted features (gitignored)
results/                metrics, plots, trained models (models gitignored)
report/                 IEEE report source
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Status

- [x] Step 1: repo scaffold + environment
- [x] Step 2: data plan + download instructions (`data/README.md`) — **the
      actual download must happen on your machine**, not in this sandbox
      (zenodo.org / datashare.ed.ac.uk / openslr.org / huggingface.co /
      kaggle.com are all blocked by this session's network policy)
- [x] Step 3: feature extraction pipeline (`src/features.py`,
      `src/extract_features.py`) — verified end-to-end on synthetic data
- [x] Step 4: train classifiers (`src/train.py`)
- [x] Step 5: evaluation + comparison (`src/evaluate.py`,
      `src/run_experiment.py`) — verified end-to-end on synthetic data
- [ ] Step 6: generalization experiment — code is ready
      (`run_experiment.py` already reports per-attack-type accuracy and
      accepts any train/test pair, e.g. 2019 LA train vs 2021 DF eval); just
      needs the real downloaded data to run on
- [ ] Step 7: report

## Running the pipeline once you have real data

```bash
# 1) subsample the official protocol to something tractable
python -m src.subsample_protocol --protocol data/protocols/ASVspoof2019.LA.cm.train.trn.txt \
    --n-per-class 1500 --output data/protocols/train_subset.txt

# 2) extract + cache features (repeat for dev / 2021 DF eval subsets)
python -m src.extract_features --protocol data/protocols/train_subset.txt \
    --audio-dir data/raw/ASVspoof2019/LA/ASVspoof2019_LA_train/flac \
    --features mfcc lfcc spectral --output data/features/train.npz

# 3) run the full comparison (MFCC+SVM, LFCC+SVM, MFCC+RF, feature combos)
python -m src.run_experiment --train-features data/features/train.npz \
    --test-features data/features/dev.npz --output-dir results/

# 4) generalization: same command, but test-features pointing at the
#    ASVspoof2021 DF eval features instead of the 2019 LA dev features
```

You can sanity-check all of this right now, without any real data, using the
synthetic generator:

```bash
python -m src.make_dummy_data --output-dir data/raw/dummy --n-per-class 30
python -m src.extract_features --protocol data/protocols/dummy_protocol.txt \
    --audio-dir data/raw/dummy --features mfcc lfcc spectral \
    --output data/features/dummy.npz
python -m src.run_experiment --train-features data/features/dummy.npz \
    --test-features data/features/dummy.npz --output-dir results/dummy_run
```
