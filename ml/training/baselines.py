"""Small, reproducible CPU baseline for chronological daily-price experiments.

This is an evaluation scaffold, not a production investment model. It uses
caller-authorized historical observations only and compares a ridge autoregression
against simple zero-return and training-mean baselines.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class Observation:
    day: date
    close: float


def load_price_csv(path: str | Path) -> list[Observation]:
    """Load a CSV with exactly the required date and close columns."""
    observations: list[Observation] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {"date", "close"}.issubset(reader.fieldnames):
            raise ValueError("CSV must contain date and close columns")
        for line_number, row in enumerate(reader, start=2):
            try:
                day = date.fromisoformat(str(row["date"]).strip())
                close = float(str(row["close"]).strip())
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid date or close on CSV line {line_number}") from exc
            if not math.isfinite(close) or close <= 0:
                raise ValueError(f"close must be finite and positive on CSV line {line_number}")
            observations.append(Observation(day, close))
    validate_observations(observations)
    return observations


def validate_observations(observations: Sequence[Observation]) -> None:
    if len(observations) < 40:
        raise ValueError("at least 40 chronological observations are required")
    dates = [item.day for item in observations]
    if dates != sorted(dates) or len(dates) != len(set(dates)):
        raise ValueError("dates must be strictly increasing with no duplicates")
    if any(not math.isfinite(item.close) or item.close <= 0 for item in observations):
        raise ValueError("close values must be finite and positive")


def _solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Solve a small dense linear system with pivoted Gaussian elimination."""
    size = len(vector)
    augmented = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            raise ValueError("training matrix is singular")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        divisor = augmented[col][col]
        augmented[col] = [value / divisor for value in augmented[col]]
        for row in range(size):
            if row == col:
                continue
            factor = augmented[row][col]
            augmented[row] = [
                current - factor * pivot_value
                for current, pivot_value in zip(augmented[row], augmented[col])
            ]
    return [augmented[row][-1] for row in range(size)]


def _metrics(actual: Sequence[float], predicted: Sequence[float]) -> dict[str, float]:
    if not actual or len(actual) != len(predicted):
        raise ValueError("actual and predicted values must be non-empty and aligned")
    errors = [guess - truth for truth, guess in zip(actual, predicted)]
    return {
        "mae": sum(abs(error) for error in errors) / len(errors),
        "rmse": math.sqrt(sum(error * error for error in errors) / len(errors)),
        "directional_accuracy": sum(
            (truth >= 0) == (guess >= 0) for truth, guess in zip(actual, predicted)
        ) / len(actual),
    }


def train_ridge_baseline(
    observations: Sequence[Observation], lookback: int = 5, ridge_alpha: float = 1.0
) -> dict[str, object]:
    """Train and evaluate a lagged-return ridge model using chronological splits."""
    validate_observations(observations)
    if not 1 <= lookback <= 20:
        raise ValueError("lookback must be between 1 and 20")
    if not math.isfinite(ridge_alpha) or ridge_alpha <= 0:
        raise ValueError("ridge_alpha must be finite and positive")

    returns = [
        observations[i].close / observations[i - 1].close - 1.0
        for i in range(1, len(observations))
    ]
    features = [returns[i - lookback : i] for i in range(lookback, len(returns))]
    targets = returns[lookback:]
    sample_count = len(targets)
    train_end = int(sample_count * 0.70)
    validation_end = int(sample_count * 0.85)
    if train_end < 20 or validation_end - train_end < 5 or sample_count - validation_end < 5:
        raise ValueError("dataset is too small for the required chronological splits")

    x_train, y_train = features[:train_end], targets[:train_end]
    x_validation, y_validation = features[train_end:validation_end], targets[train_end:validation_end]
    x_test, y_test = features[validation_end:], targets[validation_end:]

    means = [sum(row[col] for row in x_train) / train_end for col in range(lookback)]
    scales = []
    for col in range(lookback):
        variance = sum((row[col] - means[col]) ** 2 for row in x_train) / train_end
        scales.append(math.sqrt(variance) or 1.0)

    def transform(rows: Sequence[Sequence[float]]) -> list[list[float]]:
        return [[1.0] + [(row[i] - means[i]) / scales[i] for i in range(lookback)] for row in rows]

    design = transform(x_train)
    dimensions = lookback + 1
    gram = [[0.0] * dimensions for _ in range(dimensions)]
    rhs = [0.0] * dimensions
    for row, target in zip(design, y_train):
        for i in range(dimensions):
            rhs[i] += row[i] * target
            for j in range(dimensions):
                gram[i][j] += row[i] * row[j]
    for i in range(1, dimensions):
        gram[i][i] += ridge_alpha
    coefficients = _solve(gram, rhs)

    def predict(rows: Sequence[Sequence[float]]) -> list[float]:
        return [sum(a * b for a, b in zip(row, coefficients)) for row in transform(rows)]

    validation_predictions = predict(x_validation)
    test_predictions = predict(x_test)
    zero_predictions = [0.0] * len(y_test)
    train_mean = sum(y_train) / len(y_train)
    mean_predictions = [train_mean] * len(y_test)

    fingerprint_payload = [
        {"date": item.day.isoformat(), "close": format(item.close, ".12g")}
        for item in observations
    ]
    fingerprint = hashlib.sha256(
        json.dumps(fingerprint_payload, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()

    return {
        "model": "ridge_autoregression_daily_returns",
        "model_version": "0.1.0",
        "data_fingerprint_sha256": fingerprint,
        "observation_count": len(observations),
        "lookback_returns": lookback,
        "ridge_alpha": ridge_alpha,
        "split": {
            "method": "chronological_70_15_15",
            "training_examples": len(y_train),
            "validation_examples": len(y_validation),
            "test_examples": len(y_test),
            "training_end": observations[train_end + lookback].day.isoformat(),
            "test_start": observations[validation_end + lookback].day.isoformat(),
        },
        "scaler": {"means": means, "scales": scales},
        "coefficients": coefficients,
        "metrics": {
            "validation_model": _metrics(y_validation, validation_predictions),
            "test_model": _metrics(y_test, test_predictions),
            "test_zero_return_baseline": _metrics(y_test, zero_predictions),
            "test_training_mean_baseline": _metrics(y_test, mean_predictions),
        },
        "limitations": [
            "Experimental statistical baseline only; not investment advice or a trading signal.",
            "Caller must have rights to use and process the supplied historical data.",
            "No corporate-action, survivorship, liquidity, transaction-cost, or tax adjustments are performed.",
            "A chronological holdout on one series is not evidence of generalization across securities or regimes.",
            "No hyperparameter tuning was performed on the held-out test period.",
        ],
    }


def train_csv(input_path: str | Path, output_path: str | Path) -> dict[str, object]:
    result = train_ridge_baseline(load_price_csv(input_path))
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result
