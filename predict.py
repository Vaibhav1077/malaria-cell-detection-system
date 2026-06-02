from pathlib import Path

import joblib
import numpy as np
from PIL import Image

from src.config import FEATURE_IMAGE_SIZE
from src.data import extract_features_from_image
from src.utils import load_class_names, parse_predict_args


def preprocess_image(image_path: Path) -> np.ndarray:
    image = Image.open(image_path).convert("RGB")
    image = image.resize((FEATURE_IMAGE_SIZE, FEATURE_IMAGE_SIZE))
    features = extract_features_from_image(image)
    return np.expand_dims(features, axis=0)


def main() -> None:
    args = parse_predict_args()
    model = joblib.load(args.model)
    class_names = load_class_names(Path(args.class_names))
    image_batch = preprocess_image(Path(args.image))
    predicted_index = int(model.predict(image_batch)[0])
    probabilities = model.predict_proba(image_batch)[0]
    label = class_names[predicted_index]
    confidence = float(probabilities[predicted_index])

    print(f"Prediction: {label}")
    print(f"Confidence: {confidence:.4f}")
    for class_name, probability in zip(class_names, probabilities):
        print(f"Probability ({class_name}): {float(probability):.4f}")


if __name__ == "__main__":
    main()
