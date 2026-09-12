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
- [ ] Step 2: get the data
- [ ] Step 3: feature extraction
- [ ] Step 4: train classifiers
- [ ] Step 5: evaluation + comparison
- [ ] Step 6: generalization experiment
- [ ] Step 7: report
