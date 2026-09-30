from __future__ import annotations

import os
from pathlib import Path

# Limit CPU threads to reduce resource usage on Streamlit Cloud
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

import streamlit as st

st.set_page_config(
    page_title="Malaria Cell Detection",
    page_icon="🔬",
    layout="wide",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }

    /* Hero section */
    .hero {
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px;
        padding: 48px 40px;
        text-align: center;
        margin-bottom: 32px;
        border: 1px solid #1e3a5f;
    }
    .hero h1 {
        font-size: 2.8rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 12px 0;
    }
    .hero p {
        font-size: 1.1rem;
        color: #a0aec0;
        margin: 0;
        max-width: 600px;
        margin: 0 auto;
    }
    .hero .badge {
        display: inline-block;
        background: #0f3460;
        color: #60a5fa;
        border: 1px solid #1e4a8a;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 16px 4px 0 4px;
        letter-spacing: 0.5px;
    }

    /* Metric cards */
    .metric-card {
        background: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #60a5fa;
    }
    .metric-label {
        font-size: 0.82rem;
        color: #718096;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* Info cards */
    .info-card {
        background: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 24px;
        height: 100%;
    }
    .info-card h3 {
        color: #e2e8f0;
        font-size: 1rem;
        font-weight: 600;
        margin: 0 0 12px 0;
    }
    .info-card ul {
        color: #a0aec0;
        font-size: 0.9rem;
        padding-left: 18px;
        margin: 0;
        line-height: 1.8;
    }

    /* Upload zone */
    .upload-section {
        background: #1a1f2e;
        border: 2px dashed #2d4a7a;
        border-radius: 16px;
        padding: 32px;
        text-align: center;
    }

    /* Result cards */
    .result-parasitized {
        background: linear-gradient(135deg, #2d1515, #3d1a1a);
        border: 1px solid #c53030;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
    }
    .result-uninfected {
        background: linear-gradient(135deg, #0f2d1a, #133d22);
        border: 1px solid #276749;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
    }
    .result-label {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 8px 0;
    }
    .result-confidence {
        font-size: 1rem;
        color: #a0aec0;
    }

    /* Section header */
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 32px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #2d3748;
    }

    /* How it works steps */
    .step {
        display: flex;
        align-items: flex-start;
        gap: 16px;
        margin-bottom: 16px;
    }
    .step-num {
        background: #0f3460;
        color: #60a5fa;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        flex-shrink: 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #4a5568;
        font-size: 0.82rem;
        margin-top: 48px;
        padding-top: 24px;
        border-top: 1px solid #2d3748;
    }

    /* Hide streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# ── Paths ────────────────────────────────────────────────────────────────────
MODEL_PATH = Path("models/malaria_ml.joblib")
CLASS_NAMES_PATH = Path("artifacts/class_names.json")
METRICS_PATH = Path("artifacts/metrics.json")
CONFUSION_MATRIX_PATH = Path("artifacts/confusion_matrix.png")
ROC_CURVE_PATH = Path("artifacts/roc_curve.png")

# ── Validate required files ──────────────────────────────────────────────────
if not MODEL_PATH.exists():
    st.error(f"Model file not found: `{MODEL_PATH}`")
    st.stop()
if not CLASS_NAMES_PATH.exists():
    st.error(f"Class names file not found: `{CLASS_NAMES_PATH}`")
    st.stop()

try:
    import json
    import joblib
    import numpy as np
    from PIL import Image
    from src.config import FEATURE_IMAGE_SIZE
    from src.data import extract_features_from_image
    from src.utils import load_class_names
except Exception as e:
    st.error(f"Import error: {e}")
    st.stop()


# ── Cached loaders ───────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading model...")
def load_model():
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        st.error(f"Model load error: {e}")
        return None


@st.cache_data(show_spinner=False)
def load_class_names_cached():
    return load_class_names(CLASS_NAMES_PATH)


@st.cache_data(show_spinner=False)
def load_metrics():
    if METRICS_PATH.exists():
        with open(METRICS_PATH) as f:
            return json.load(f)
    return {}


# ── Inference helpers ────────────────────────────────────────────────────────
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


# ── Load resources ───────────────────────────────────────────────────────────
model = load_model()
if model is None:
    st.stop()
class_names = load_class_names_cached()
metrics = load_metrics()

# ════════════════════════════════════════════════════════════════════════════
# HERO SECTION
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <h1>🔬 Malaria Cell Detection System</h1>
    <p>AI-powered blood smear analysis using classical machine learning to detect malaria parasites in red blood cells.</p>
    <span class="badge">🧬 Classical ML</span>
    <span class="badge">📊 SVM / Logistic Regression</span>
    <span class="badge">🩸 Blood Smear Analysis</span>
    <span class="badge">⚡ Real-time Prediction</span>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# METRICS ROW
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Model Performance</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
metric_items = [
    (c1, "Test Accuracy",  f"{metrics.get('accuracy', 0)*100:.1f}%"),
    (c2, "Precision",      f"{metrics.get('precision', 0)*100:.1f}%"),
    (c3, "Recall",         f"{metrics.get('recall', 0)*100:.1f}%"),
    (c4, "F1-Score",       f"{metrics.get('f1_score', 0)*100:.1f}%"),
    (c5, "ROC-AUC",        f"{metrics.get('roc_auc', 0)*100:.1f}%"),
]
for col, label, value in metric_items:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# INFO CARDS ROW
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🛠️ About This Project</div>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("""
    <div class="info-card">
        <h3>🧠 How It Works</h3>
        <ul>
            <li>Image resized to 32×32 pixels</li>
            <li>Handcrafted features extracted</li>
            <li>Color histograms (RGB channels)</li>
            <li>Texture &amp; intensity statistics</li>
            <li>ML model classifies the cell</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="info-card">
        <h3>⚙️ Tech Stack</h3>
        <ul>
            <li>Python · scikit-learn · NumPy</li>
            <li>Pillow (image processing)</li>
            <li>Streamlit (web interface)</li>
            <li>Joblib (model serialization)</li>
            <li>NIH Cell Images Dataset</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="info-card">
        <h3>🩺 Classes Detected</h3>
        <ul>
            <li><b style="color:#fc8181;">🔴 Parasitized</b> — Cell infected with <i>Plasmodium</i> malaria parasite</li>
            <li><b style="color:#68d391;">🟢 Uninfected</b> — Healthy red blood cell, no parasite detected</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PREDICTION SECTION
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🖼️ Try It — Upload a Cell Image</div>', unsafe_allow_html=True)

upload_col, result_col = st.columns([1, 1], gap="large")

with upload_col:
    st.markdown("""
    <div style="color:#a0aec0; font-size:0.9rem; margin-bottom:12px;">
        Upload a microscopic blood smear image (PNG / JPG / JPEG).
        The model will analyze the cell and classify it instantly.
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Cell Image", use_container_width=True)

        predict_btn = st.button("🔍 Analyze Cell", type="primary", use_container_width=True)
    else:
        st.markdown("""
        <div style="
            border: 2px dashed #2d4a7a;
            border-radius: 12px;
            padding: 48px 24px;
            text-align: center;
            color: #4a5568;
        ">
            <div style="font-size:3rem;">🩸</div>
            <div style="margin-top:12px; font-size:0.95rem;">Drop your cell image here</div>
            <div style="font-size:0.8rem; margin-top:6px;">Supports PNG, JPG, JPEG</div>
        </div>
        """, unsafe_allow_html=True)
        predict_btn = False

with result_col:
    if uploaded_file is not None and predict_btn:
        with st.spinner("Analyzing cell..."):
            try:
                label, confidence, probabilities = predict_image(model, class_names, image)

                is_parasitized = label.lower() == "parasitized"
                card_class = "result-parasitized" if is_parasitized else "result-uninfected"
                icon = "🦠" if is_parasitized else "✅"
                color = "#fc8181" if is_parasitized else "#68d391"

                st.markdown(f"""
                <div class="{card_class}">
                    <div style="font-size:3rem;">{icon}</div>
                    <div class="result-label" style="color:{color};">{label}</div>
                    <div class="result-confidence">Confidence: {confidence:.1%}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.write("**Probability Breakdown:**")
                for name, prob in zip(class_names, probabilities):
                    bar_color = "#fc8181" if name.lower() == "parasitized" else "#68d391"
                    st.markdown(f"`{name}`")
                    st.progress(float(prob))
                    st.caption(f"{float(prob):.2%}")

            except Exception as e:
                st.error(f"Prediction error: {e}")

    elif uploaded_file is None:
        st.markdown("""
        <div style="
            background: #1a1f2e;
            border: 1px solid #2d3748;
            border-radius: 12px;
            padding: 48px 24px;
            text-align: center;
            color: #4a5568;
            height: 100%;
        ">
            <div style="font-size:3rem;">📊</div>
            <div style="margin-top:16px; font-size:1rem; color:#718096;">
                Results will appear here
            </div>
            <div style="font-size:0.85rem; margin-top:8px;">
                Upload an image and click Analyze
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif uploaded_file is not None and not predict_btn:
        st.markdown("""
        <div style="
            background: #1a1f2e;
            border: 1px solid #2d4a7a;
            border-radius: 12px;
            padding: 48px 24px;
            text-align: center;
        ">
            <div style="font-size:3rem;">👆</div>
            <div style="margin-top:16px; font-size:1rem; color:#a0aec0;">
                Click <b>Analyze Cell</b> to run prediction
            </div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# EVALUATION ARTIFACTS
# ════════════════════════════════════════════════════════════════════════════
if CONFUSION_MATRIX_PATH.exists() or ROC_CURVE_PATH.exists():
    st.markdown('<div class="section-title">📉 Evaluation Artifacts</div>', unsafe_allow_html=True)
    art_col1, art_col2 = st.columns(2)
    if CONFUSION_MATRIX_PATH.exists():
        with art_col1:
            st.image(str(CONFUSION_MATRIX_PATH), caption="Confusion Matrix", use_container_width=True)
    if ROC_CURVE_PATH.exists():
        with art_col2:
            st.image(str(ROC_CURVE_PATH), caption="ROC Curve", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
    Built with Python · scikit-learn · Streamlit &nbsp;|&nbsp;
    Dataset: NIH Cell Images for Detecting Malaria &nbsp;|&nbsp;
    Classical ML — No deep learning
</div>
""", unsafe_allow_html=True)
