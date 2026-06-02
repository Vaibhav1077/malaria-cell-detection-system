from pathlib import Path

import joblib

from src.config import TrainConfig
from src.data import load_dataset_splits
from src.evaluate import evaluate_and_save_reports
from src.model import build_model
from src.utils import ensure_dirs, parse_train_args, save_class_names, save_run_config


def main() -> None:
    args = parse_train_args()
    config = TrainConfig.from_args(args)
    ensure_dirs(config.artifacts_dir, config.model_dir)
    save_run_config(config)

    X_train, X_val, X_test, y_train, y_val, y_test, class_names = load_dataset_splits(config)
    save_class_names(class_names, Path(config.artifacts_dir) / "class_names.json")
    model = build_model(config)
    model.fit(X_train, y_train)

    model_path = Path(config.model_dir) / config.model_name
    joblib.dump(model, model_path)

    evaluate_and_save_reports(model, X_val, X_test, y_val, y_test, class_names, config)

    print(f"Training complete. Model saved to: {model_path}")
    print(f"Artifacts saved under: {config.artifacts_dir}")


if __name__ == "__main__":
    main()
