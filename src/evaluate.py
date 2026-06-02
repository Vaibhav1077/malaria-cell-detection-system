from __future__ import annotations

import json
import os
from pathlib import Path

_matplotlib_cache_dir = Path("artifacts") / "matplotlib-cache"
_matplotlib_cache_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_matplotlib_cache_dir))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from src.config import TrainConfig


def evaluate_and_save_reports(model, X_val, X_test, y_val, y_test, class_names, config: TrainConfig) -> None:
    y_true = y_test
    y_pred = model.predict(X_test)
    y_scores = model.predict_proba(X_test)[:, 1]

    metrics = {
        "validation_accuracy": float(model.score(X_val, y_val)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred)),
        "recall": float(recall_score(y_true, y_pred)),
        "f1_score": float(f1_score(y_true, y_pred)),
        "roc_auc": float(roc_auc_score(y_true, y_scores)),
    }

    artifacts_dir = Path(config.artifacts_dir)
    with open(artifacts_dir / "metrics.json", "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
    pd.DataFrame(report).transpose().to_csv(artifacts_dir / "classification_report.csv")

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(artifacts_dir / "confusion_matrix.png", dpi=200)
    plt.close()

    fpr, tpr, _ = roc_curve(y_true, y_scores)
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label=f"AUC = {metrics['roc_auc']:.4f}")
    plt.plot([0, 1], [0, 1], linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(artifacts_dir / "roc_curve.png", dpi=200)
    plt.close()
