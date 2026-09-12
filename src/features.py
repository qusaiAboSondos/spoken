"""Speech/spectral feature extraction for the real-vs-AI-generated speech task.

All extractors return a single fixed-length vector per utterance (statistics
pooling: mean + std across frames), so they can be fed straight into
classical ML classifiers (SVM, Random Forest) regardless of utterance length.

Implemented, per the project brief:
- Cepstral: MFCC, LFCC
- Spectral: centroid, bandwidth, roll-off, flux
- Time-domain: short-time energy, zero-crossing rate
"""
from __future__ import annotations

import numpy as np
import librosa
from scipy.fftpack import dct

SR = 16000          # ASVspoof audio is 16 kHz
N_FFT = 512         # 32 ms at 16 kHz
HOP_LENGTH = 160    # 10 ms hop
WIN_LENGTH = 400    # 25 ms window


def load_audio(path: str, sr: int = SR) -> np.ndarray:
    y, _sr = librosa.load(path, sr=sr, mono=True)
    return y


def _pool(mat: np.ndarray) -> np.ndarray:
    """mat: (n_coeffs, n_frames) -> (2*n_coeffs,) mean+std pooled vector."""
    return np.concatenate([mat.mean(axis=1), mat.std(axis=1)])


def _with_deltas(mat: np.ndarray) -> np.ndarray:
    """Pool static + delta + delta-delta coefficients (standard in ASR/anti-spoofing)."""
    delta = librosa.feature.delta(mat, order=1)
    delta2 = librosa.feature.delta(mat, order=2)
    return np.concatenate([_pool(mat), _pool(delta), _pool(delta2)])


def extract_mfcc(y: np.ndarray, sr: int = SR, n_mfcc: int = 20) -> np.ndarray:
    mfcc = librosa.feature.mfcc(
        y=y, sr=sr, n_mfcc=n_mfcc, n_fft=N_FFT, hop_length=HOP_LENGTH, win_length=WIN_LENGTH
    )
    return _with_deltas(mfcc)


def _linear_filterbank(sr: int, n_fft: int, n_filters: int) -> np.ndarray:
    """Triangular filters evenly spaced on a LINEAR frequency scale (unlike Mel).

    This is the key difference between LFCC and MFCC: LFCC preserves
    resolution at high frequencies, which is where TTS/vocoder artifacts
    often show up.
    """
    n_bins = n_fft // 2 + 1
    freqs = np.linspace(0, sr / 2, n_bins)
    edges = np.linspace(0, sr / 2, n_filters + 2)
    fb = np.zeros((n_filters, n_bins))
    for i in range(n_filters):
        lo, mid, hi = edges[i], edges[i + 1], edges[i + 2]
        rising = (freqs >= lo) & (freqs <= mid)
        falling = (freqs >= mid) & (freqs <= hi)
        if mid > lo:
            fb[i, rising] = (freqs[rising] - lo) / (mid - lo)
        if hi > mid:
            fb[i, falling] = (hi - freqs[falling]) / (hi - mid)
    return fb


def extract_lfcc(y: np.ndarray, sr: int = SR, n_lfcc: int = 20, n_filters: int = 40) -> np.ndarray:
    spec = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH, win_length=WIN_LENGTH)) ** 2
    fb = _linear_filterbank(sr, N_FFT, n_filters)
    filtered = np.dot(fb, spec)                      # (n_filters, n_frames)
    log_energy = np.log(filtered + 1e-10)
    lfcc = dct(log_energy, type=2, axis=0, norm="ortho")[:n_lfcc]
    return _with_deltas(lfcc)


def extract_spectral(y: np.ndarray, sr: int = SR) -> np.ndarray:
    stft_mag = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH, win_length=WIN_LENGTH))

    centroid = librosa.feature.spectral_centroid(S=stft_mag, sr=sr)
    bandwidth = librosa.feature.spectral_bandwidth(S=stft_mag, sr=sr)
    rolloff = librosa.feature.spectral_rolloff(S=stft_mag, sr=sr)

    # spectral flux: frame-to-frame L2 distance between normalized magnitude spectra
    norm_spec = stft_mag / (np.linalg.norm(stft_mag, axis=0, keepdims=True) + 1e-10)
    flux = np.sqrt(np.sum(np.diff(norm_spec, axis=1) ** 2, axis=0))
    flux = np.concatenate([[0.0], flux])[None, :]  # keep same n_frames as the rest

    zcr = librosa.feature.zero_crossing_rate(y, frame_length=WIN_LENGTH, hop_length=HOP_LENGTH)

    # short-time energy (sum of squared samples per frame)
    frames = librosa.util.frame(
        np.pad(y, (0, max(0, WIN_LENGTH - len(y)))), frame_length=WIN_LENGTH, hop_length=HOP_LENGTH
    )
    energy = np.sum(frames.astype(np.float64) ** 2, axis=0, keepdims=True)
    # align frame counts (librosa.util.frame can produce one fewer/more frame than
    # the STFT-based features depending on padding); trim to the shortest.
    n = min(centroid.shape[1], energy.shape[1])

    feats = np.vstack(
        [centroid[:, :n], bandwidth[:, :n], rolloff[:, :n], flux[:, :n], zcr[:, :n], energy[:, :n]]
    )
    return _pool(feats)


FEATURE_EXTRACTORS = {
    "mfcc": extract_mfcc,
    "lfcc": extract_lfcc,
    "spectral": extract_spectral,
}


def extract_features(y: np.ndarray, sr: int, feature_names: list[str]) -> dict[str, np.ndarray]:
    """Extract each requested feature type independently, so callers can cache
    them separately and combine subsets later without re-extracting."""
    return {name: FEATURE_EXTRACTORS[name](y, sr) for name in feature_names}
