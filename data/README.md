# Getting the data

**Important:** this sandboxed dev session cannot reach the dataset hosts
(zenodo.org, datashare.ed.ac.uk, openslr.org, huggingface.co, kaggle.com are
all blocked by network policy here). Run the commands below **on your own
machine** (or Google Colab / Kaggle), not inside this session. The code in
`src/` works the same wherever you run it — only the download step needs to
happen elsewhere.

## 1. ASVspoof 2019 LA (train + dev) — used for training

Source: University of Edinburgh DataShare, ASVspoof 2019 database.
Page: https://datashare.ed.ac.uk/handle/10283/3336

```bash
mkdir -p data/raw
cd data/raw
wget https://datashare.ed.ac.uk/bitstream/handle/10283/3336/LA.zip
unzip LA.zip -d ASVspoof2019
```

This gives you (inside `ASVspoof2019/LA/`):
- `ASVspoof2019_LA_train/flac/*.flac` + protocol
  `ASVspoof2019_LA_cm_protocols/ASVspoof2019.LA.cm.train.trn.txt`
- `ASVspoof2019_LA_dev/flac/*.flac` + protocol
  `ASVspoof2019_LA_cm_protocols/ASVspoof2019.LA.cm.dev.trl.txt`

Copy (or symlink) the protocol files into `data/protocols/` so they're tracked
alongside the code (they're small text files, safe to commit):

```bash
cp data/raw/ASVspoof2019/LA/ASVspoof2019_LA_cm_protocols/*.txt data/protocols/
```

## 2. ASVspoof 2021 DF (eval) — used for the generalization test

Source: Zenodo, ASVspoof 2021 Challenge - Speech Deepfake Database.
Page: https://zenodo.org/records/4835108
Evaluation keys/labels: https://www.asvspoof.org/index2021.html

The full DF eval set is very large (600k+ files). **Do not download all of
it.** Download the archive, then use `src/subsample_protocol.py` (see step
3) to pick a few thousand files per class before extracting only those FLACs
— or if the archive is split into parts, only fetch/extract the first part.

```bash
mkdir -p data/raw
cd data/raw
wget <DF part_00 archive URL from the Zenodo page>
unzip <archive>.zip -d ASVspoof2021DF
```

You also need the eval keys (bona fide/spoof ground truth + attack/generator
labels), published separately (not bundled in the audio archive) — download
them from the asvspoof.org keys page linked above and place them at
`data/protocols/ASVspoof2021.DF.cm.eval.trl.txt`.

## 3. Subsampling (recommended, keeps things tractable in a week)

Once you have the protocol files in `data/protocols/`, create a manageable
subset (e.g. 1500 bona fide + 1500 spoof for train, similar for dev, and
~1000/1000 for the 2021 DF eval generalization test):

```bash
python src/subsample_protocol.py \
  --protocol data/protocols/ASVspoof2019.LA.cm.train.trn.txt \
  --dataset asvspoof2019 \
  --n-per-class 1500 \
  --output data/protocols/train_subset.txt
```

Then only extract/keep the FLAC files listed in `train_subset.txt` from the
archive (or just leave the full archive and let `src/dataset.py` read by
file id — it only opens the files it needs).

## 4. Sanity-check without the real dataset

`src/make_dummy_data.py` generates a handful of synthetic sine/noise "audio"
files with a matching protocol file, purely so the rest of the pipeline
(feature extraction → training → evaluation) can be run and tested end to
end without any download. Useful for verifying the code works before you
have the real data:

```bash
python src/make_dummy_data.py --output-dir data/raw/dummy --n-per-class 20
```
