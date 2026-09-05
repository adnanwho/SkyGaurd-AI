from __future__ import annotations

import pandas as pd


def evaluate_detection(data: pd.DataFrame) -> dict[str, float | int]:
    truth = data["ground_truth"].ne("NORMAL")
    predicted_column = "Final_Anomaly" if "Final_Anomaly" in data.columns else "Ensemble_Anomaly"
    predicted = data[predicted_column].astype(bool)
    tp = int((truth & predicted).sum())
    fp = int((~truth & predicted).sum())
    fn = int((truth & ~predicted).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    total_normal = int((~truth).sum())
    total_anomalous = int(truth.sum())
    metrics: dict[str, float | int] = {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": int((~truth & ~predicted).sum()),
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "false_positive_rate": fp / total_normal if total_normal else 0.0,
        "false_negative_rate": fn / total_anomalous if total_anomalous else 0.0,
    }
    if "ground_truth" in data:
        for label in sorted(set(data["ground_truth"]) - {"NORMAL"}):
            actual = data["ground_truth"].eq(label)
            label_tp = int((predicted & actual).sum())
            label_fn = int((actual & ~predicted).sum())
            label_fp = int((predicted & ~actual).sum())
            label_precision = label_tp / (label_tp + label_fp) if label_tp + label_fp else 0.0
            label_recall = label_tp / (label_tp + label_fn) if label_tp + label_fn else 0.0
            metrics[f"{label.lower()}_precision"] = label_precision
            metrics[f"{label.lower()}_recall"] = label_recall
            metrics[f"{label.lower()}_f1"] = 2 * label_precision * label_recall / (label_precision + label_recall) if label_precision + label_recall else 0.0
        metrics["root_cause_confusion_matrix"] = pd.crosstab(
            data["ground_truth"], predicted.astype(str), rownames=["ground_truth"], colnames=["predicted"]
        ).to_dict()
    if "event_type" in data:
        actual_event = data["ground_truth"].eq("WEATHER_EVENT") if "ground_truth" in data else pd.Series(False, index=data.index)
        predicted_event = data["event_type"].eq("WEATHER_EVENT")
        metrics["weather_event_recall"] = int((actual_event & predicted_event).sum()) / int(actual_event.sum()) if actual_event.any() else 0.0
        if "ground_truth" in data:
            metrics["event_fault_confusion_matrix"] = pd.crosstab(
                data["ground_truth"].where(actual_event, "NOT_WEATHER_EVENT"),
                data["event_type"],
            ).to_dict()
    if "processing_ms" in data and len(data):
        latency = pd.to_numeric(data["processing_ms"], errors="coerce").dropna()
        if not latency.empty:
            metrics["latency_mean_ms"] = float(latency.mean())
            metrics["latency_median_ms"] = float(latency.median())
            metrics["latency_p95_ms"] = float(latency.quantile(0.95))
    return metrics
