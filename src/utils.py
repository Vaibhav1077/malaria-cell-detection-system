from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_train_args():
    parser = argparse.ArgumentParser(description="Train the malaria ML model.")
    parser.add_argument("--data-dir", default="data/cell_images", help="Path to dataset root.")
    parser.add_argument(
        "--model-type",
        default="svm",
        choices=["svm", "random_forest", "logistic_regression"],
        help="Classical ML model to train.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--artifacts-dir", default="artifacts", help="Directory for reports.")
    parser.add_argument("--model-dir", default="models", help="Directory for saved models.")
    parser.add_argument("--model-name", default="malaria_ml.joblib", help="Saved model filename.")
    return parser.parse_args()


def parse_predict_args():
    parser = argparse.ArgumentParser(description="Predict malaria infection from a single image.")
    parser.add_argument("--image", required=True, help="Path to input image.")
    parser.add_argument("--model", required=True, help="Path to trained model.")
    parser.add_argument(
        "--class-names",
        default="artifacts/class_names.json",
        help="Path to saved class name mapping.",
    )
    return parser.parse_args()


def ensure_dirs(*paths: str) -> None:
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def save_run_config(config) -> None:
    config_path = Path(config.artifacts_dir) / "run_config.json"
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(config.asdict(), file, indent=2)


def save_class_names(class_names: list[str], output_path: Path) -> None:
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(class_names, file, indent=2)


def load_class_names(path: Path) -> list[str]:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
