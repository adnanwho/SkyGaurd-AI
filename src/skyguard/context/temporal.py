from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
import numpy as np

from ..config import DEFAULT_CONFIG
from ..utils.paths import resolve_project_path


@dataclass(frozen=True)
class TemporalModelStatus:
    available: bool
    method: str
    message: str


def temporal_model_status() -> TemporalModelStatus:
    """Report whether the optional LSTM dependency is available."""
    try:
        import tensorflow  # noqa: F401
    except ImportError:
        return TemporalModelStatus(False, "lstm_autoencoder", "TensorFlow is not installed; temporal model is unavailable.")
    return TemporalModelStatus(True, "lstm_autoencoder", "TensorFlow is available; training remains an explicit opt-in operation.")


def score_sequences(data: pd.DataFrame) -> dict[str, Any]:
    """Safe optional boundary for future LSTM sequence scoring."""
    status = temporal_model_status()
    return {
        "available": status.available,
        "method": status.method,
        "message": status.message,
        "scores": [] if not status.available else [],
    }


def _tensorflow() -> Any:
    try:
        import tensorflow as tf
    except ImportError as error:
        raise RuntimeError("TensorFlow is not installed; install the optional temporal-model dependency to use the LSTM autoencoder.") from error
    return tf


def make_sequences(values: pd.DataFrame, window: int = 12) -> Any:
    """Create overlapping numeric sequences for LSTM training/scoring."""
    if window < 2 or len(values) <= window:
        raise ValueError("values must contain more rows than the sequence window")
    numeric = values.select_dtypes(include="number").astype("float32").interpolate(limit_direction="both")
    return numeric, np.stack(
        [numeric.iloc[index - window:index].to_numpy() for index in range(window, len(numeric))]
    )


def train_lstm_autoencoder(
    values: pd.DataFrame,
    output_path: str = str(DEFAULT_CONFIG.paths.model_dir / "lstm_autoencoder.keras"),
    window: int = 12,
    epochs: int = 10,
) -> dict[str, Any]:
    """Train an optional LSTM autoencoder on clean numeric sequences."""
    tf = _tensorflow()
    _, sequences = make_sequences(values, window)
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(sequences.shape[1], sequences.shape[2])),
        tf.keras.layers.LSTM(32, activation="tanh", return_sequences=False),
        tf.keras.layers.RepeatVector(sequences.shape[1]),
        tf.keras.layers.LSTM(32, activation="tanh", return_sequences=True),
        tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(sequences.shape[2])),
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(sequences, sequences, epochs=epochs, batch_size=32, verbose=0)
    output = resolve_project_path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    model.save(output)
    errors = np.mean(np.square(sequences - model.predict(sequences, verbose=0)), axis=(1, 2))
    return {"available": True, "model_path": str(output), "window": window, "training_rows": len(sequences), "threshold": float(np.quantile(errors, 0.98))}


def score_lstm_autoencoder(values: pd.DataFrame, model_path: str = str(DEFAULT_CONFIG.paths.model_dir / "lstm_autoencoder.keras"), window: int = 12) -> pd.DataFrame:
    """Score sequences with a trained optional LSTM autoencoder."""
    tf = _tensorflow()
    numeric, sequences = make_sequences(values, window)
    model = tf.keras.models.load_model(resolve_project_path(model_path))
    reconstructed = model.predict(sequences, verbose=0)
    errors = np.mean(np.square(sequences - reconstructed), axis=(1, 2))
    return pd.DataFrame({"row_index": numeric.index[window:], "LSTM_Reconstruction_Error": errors})
