from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from src.config import TrainConfig


def extract_features_from_image(image: Image.Image) -> np.ndarray:
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    gray = np.asarray(image.convert("L"), dtype=np.float32) / 255.0

    flat_gray = gray.flatten()
    color_stats = np.concatenate([rgb.mean(axis=(0, 1)), rgb.std(axis=(0, 1))])
    hist_features = []
    for channel in range(3):
        hist, _ = np.histogram(rgb[:, :, channel], bins=16, range=(0.0, 1.0), density=True)
        hist_features.append(hist)

    texture_stats = np.array(
        [
            float(gray.mean()),
            float(gray.std()),
            float(np.percentile(gray, 25)),
            float(np.percentile(gray, 50)),
            float(np.percentile(gray, 75)),
        ],
        dtype=np.float32,
    )
    return np.concatenate([flat_gray, color_stats, *hist_features, texture_stats]).astype(np.float32)


def load_dataset_splits(config: TrainConfig):
    from sklearn.model_selection import train_test_split
    data_dir = Path(config.data_dir)
    if not data_dir.exists():
        raise FileNotFoundError(
            f"Dataset directory not found: {data_dir}. "
            "Place the NIH malaria dataset under data/cell_images."
        )

    class_names = sorted([path.name for path in data_dir.iterdir() if path.is_dir()])
    if len(class_names) != 2:
        raise ValueError("Expected exactly two class folders under data/cell_images.")

    features = []
    labels = []
    for label_index, class_name in enumerate(class_names):
        class_dir = data_dir / class_name
        for image_path in class_dir.glob("*"):
            if image_path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
                continue
            image = Image.open(image_path).convert("RGB").resize((config.image_size, config.image_size))
            features.append(extract_features_from_image(image))
            labels.append(label_index)

    if not features:
        raise ValueError("No images found in dataset folders.")

    X = np.asarray(features, dtype=np.float32)
    y = np.asarray(labels, dtype=np.int32)

    temp_size = config.val_split + config.test_split
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=temp_size,
        random_state=config.seed,
        stratify=y,
    )

    val_ratio_in_temp = config.val_split / temp_size
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=1 - val_ratio_in_temp,
        random_state=config.seed,
        stratify=y_temp,
    )

    return X_train, X_val, X_test, y_train, y_val, y_test, class_names
