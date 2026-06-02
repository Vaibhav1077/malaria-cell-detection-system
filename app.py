from pathlib import Path

import joblib
import numpy as np
import streamlit as st
from PIL import Image

from src.config import FEATURE_IMAGE_SIZE
from src.data import extract_features_from_image
from src.utils import load_class_names

MODEL_PATH = Path("models/malaria_ml.joblib")
CLASS_NAMES_PATH = Path("artifacts/class_names.json")
DEMO_IMAGES = {
    "Parasitized demo sample": Path(
        "data/cell_images/Parasitized/C100P61ThinF_IMG_20150918_144348_cell_144.png"
    ),
    "Uninfected demo sample": Path(
        "data/cell_images/Uninfected/C102P63ThinF_IMG_20150918_161508_cell_37.png"
    ),
}


@st.cache_resource
def load_model(model_mtime: float):
    return joblib.load(MODEL_PATH)


def preprocess_image(image: Image.Image) -> np.ndarray:
    image = image.convert("RGB").resize((FEATURE_IMAGE_SIZE, FEATURE_IMAGE_SIZE))
    features = extract_features_from_image(image)
    return np.expand_dims(features, axis=0)


def predict_image(model, class_names: list[str], image: Image.Image):
    batch = preprocess_image(image)
    predicted_index = int(model.predict(batch)[0])
    probabilities = model.predict_proba(batch)[0]
    label = class_names[predicted_index]
    confidence = float(probabilities[predicted_index])
    return label, confidence, probabilities


def show_prediction(label: str, confidence: float, probabilities, class_names: list[str]) -> None:
    st.subheader(f"Prediction: {label}")
    st.write(f"Confidence: `{confidence:.2%}`")
    st.progress(min(max(confidence, 0.0), 1.0))
    st.write("Class probabilities:")
    for class_name, probability in zip(class_names, probabilities):
        st.write(f"- {class_name}: `{float(probability):.2%}`")


st.set_page_config(page_title="Malaria Detection", page_icon="M", layout="centered")
st.title("Malaria Parasite Detection")
st.write("Upload a blood smear cell image to classify it as Parasitized or Uninfected using a classical ML model.")

if not MODEL_PATH.exists():
    st.warning("Model file not found. Train the model first using `python train.py`.")
elif not CLASS_NAMES_PATH.exists():
    st.warning("Class mapping not found. Re-run training to generate `artifacts/class_names.json`.")
else:
    model = load_model(MODEL_PATH.stat().st_mtime)
    class_names = load_class_names(CLASS_NAMES_PATH)

    st.subheader("Presentation demo samples")
    demo_choice = st.selectbox("Choose a tested sample", ["None", *DEMO_IMAGES.keys()])
    if demo_choice != "None":
        demo_path = DEMO_IMAGES[demo_choice]
        if not demo_path.exists():
            st.info("Demo dataset images are not available. Upload an image or add the dataset under `data/cell_images`.")
        else:
            image = Image.open(demo_path)
            st.image(image, caption=demo_path.name, use_container_width=True)
            label, confidence, probabilities = predict_image(model, class_names, image)
            show_prediction(label, confidence, probabilities, class_names)

    st.divider()
    uploaded_file = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded image", use_container_width=True)

        if st.button("Predict", type="primary"):
            label, confidence, probabilities = predict_image(model, class_names, image)
            show_prediction(label, confidence, probabilities, class_names)
