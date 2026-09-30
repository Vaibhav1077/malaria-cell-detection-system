from __future__ import annotations

import gc
import os
from pathlib import Path

# Set env vars before any imports to reduce memory overhead
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import joblib
import numpy as np
import streamlit as st
from PIL import Image

from src.config import FEATURE_IMAGE_SIZE
from src.data import extract_features_from_image
from src.utils import load_class_names

MODEL_PATH = Path("models/malaria_ml.joblib")
CLASS_NAMES_PATH = Path("artifacts/class_names.json")


@st.cache_resource(show_spinner="Loading model...")
def load_model():
    model = joblib.load(MODEL_PATH)
    gc.collect()
    return model


@st.cache_data(show_spinner=False)
def load_class_names_cached():
    return load_class_names(CLASS_NAMES_PATH)


def preprocess_image(image: Image.Image) -> np.ndarray:
    image = image.convert("RGB").resize((FEATURE_IMAGE_SIZE, FEATURE_IMAGE_SIZE))
    features = extract_features_from_image(image)
    return np.expand_dims(features, axis=0)


def predict_image(model, class_names: list, image: Image.Image):
    batch = preprocess_image(image)
    predicted_index = int(model.predict(batch)[0])
    probabilities = model.predict_proba(batch)[0]
    label = class_names[predicted_index]
    confidence = float(probabilities[predicted_index])
    return label, confidence, probabilities


def show_prediction(label: str, confidence: float, probabilities, class_names: list) -> None:
    if label.lower() == "parasitized":
        st.error(f"Prediction: {label}")
    else:
        st.success(f"Prediction: {label}")
    st.write(f"Confidence: `{confidence:.2%}`")
    st.progress(min(max(confidence, 0.0), 1.0))
    st.write("Class probabilities:")
    for class_name, probability in zip(class_names, probabilities):
        st.write(f"- {class_name}: `{float(probability):.2%}`")


# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Malaria Detection",
    page_icon="🔬",
    layout="centered",
)

st.title("🔬 Malaria Parasite Detection")
st.write(
    "Upload a blood smear cell image to classify it as "
    "**Parasitized** or **Uninfected** using a classical ML model."
)

# ── Checks ───────────────────────────────────────────────────────────────────
if not MODEL_PATH.exists():
    st.error("Model file not found: `models/malaria_ml.joblib`")
    st.stop()

if not CLASS_NAMES_PATH.exists():
    st.error("Class names file not found: `artifacts/class_names.json`")
    st.stop()

# ── Load resources ───────────────────────────────────────────────────────────
model = load_model()
class_names = load_class_names_cached()

# ── Upload & predict ─────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload a cell image", type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded image", use_container_width=True)

    if st.button("Predict", type="primary"):
        with st.spinner("Analyzing..."):
            label, confidence, probabilities = predict_image(model, class_names, image)
        show_prediction(label, confidence, probabilities, class_names)
        gc.collect()
