from __future__ import annotations

import json
import os
from pathlib import Path

# Limit CPU threads — keeps Streamlit Cloud throttle away
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
    initial_sidebar_state="collapsed",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #080c14; }

/* hide streamlit chrome */
#MainMenu, footer, .stDeployButton { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* ── hero ── */
.hero {
    background: linear-gradient(135deg, #0d1b2a 0%, #112240 60%, #0a3d62 100%);
    border: 1px solid #1e3a5f;
    border-radius: 20px;
    padding: 52px 40px 44px;
    text-align: center;
    margin-bottom: 36px;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: #f0f4ff;
    margin: 0 0 10px;
    letter-spacing: -0.5px;
}
.hero-sub {
    font-size: 1.05rem;
    color: #8899aa;
    max-width: 580px;
    margin: 0 auto 20px;
    line-height: 1.6;
}
.badge {
    display: inline-block;
    background: rgba(96,165,250,0.12);
    color: #60a5fa;
    border: 1px solid rgba(96,165,250,0.25);
    border-radius: 999px;
    padding: 5px 14px;
    font-size: 0.76rem;
    font-weight: 600;
    margin: 4px 3px;
    letter-spacing: 0.4px;
}

/* ── section title ── */
.sec-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #c8d8e8;
    letter-spacing: 0.3px;
    margin: 36px 0 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid #1e2d40;
}

/* ── metric cards ── */
.metric-grid { display: flex; gap: 12px; flex-wrap: wrap; }
.mcard {
    flex: 1;
    min-width: 110px;
    background: #0d1b2a;
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 20px 12px;
    text-align: center;
}
.mcard-val {
    font-size: 1.75rem;
    font-weight: 800;
    color: #60a5fa;
    line-height: 1;
}
.mcard-lbl {
    font-size: 0.72rem;
    color: #4a6580;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 6px;
}

/* ── info cards ── */
.icard {
    background: #0d1b2a;
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 24px 20px;
    height: 100%;
}
.icard-title {
    font-size: 0.92rem;
    font-weight: 700;
    color: #c8d8e8;
    margin: 0 0 14px;
}
.icard ul {
    color: #7a9ab8;
    font-size: 0.86rem;
    padding-left: 18px;
    margin: 0;
    line-height: 2;
}

/* ── upload panel ── */
.upload-hint {
    color: #5a7a96;
    font-size: 0.88rem;
    line-height: 1.6;
    margin-bottom: 14px;
}
.drop-zone {
    border: 2px dashed #1e3a5f;
    border-radius: 14px;
    padding: 52px 20px;
    text-align: center;
    color: #2a4a6a;
}
.drop-icon { font-size: 2.6rem; }
.drop-text { margin-top: 10px; font-size: 0.92rem; color: #3a5a7a; }
.drop-hint { font-size: 0.78rem; margin-top: 4px; color: #2a4060; }

/* ── await panel ── */
.await-box {
    background: #0d1b2a;
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 60px 20px;
    text-align: center;
    color: #2a4a6a;
    height: 100%;
}
.await-icon { font-size: 2.6rem; }
.await-text { margin-top: 14px; font-size: 0.95rem; color: #4a6a8a; }
.await-hint { font-size: 0.82rem; margin-top: 6px; color: #2a4060; }

/* ── result cards ── */
.res-bad {
    background: linear-gradient(135deg, #1a0808, #2a1010);
    border: 1px solid #7f1d1d;
    border-radius: 14px;
    padding: 28px 20px;
    text-align: center;
}
.res-good {
    background: linear-gradient(135deg, #081a0e, #102a16);
    border: 1px solid #14532d;
    border-radius: 14px;
    padding: 28px 20px;
    text-align: center;
}
.res-icon { font-size: 2.8rem; }
.res-label { font-size: 1.6rem; font-weight: 800; margin: 8px 0 4px; }
.res-conf { font-size: 0.9rem; color: #7a9ab8; }

/* ── footer ── */
.footer {
    text-align: center;
    color: #253545;
    font-size: 0.8rem;
    margin-top: 52px;
    padding-top: 20px;
    border-top: 1px solid #111e2d;
}
</style>
""", unsafe_allow_html=True)

# ── Paths ────────────────────────────────────────────────────────────────────
MODEL_PATH        = Path("models/malaria_ml.joblib")
CLASS_NAMES_PATH  = Path("artifacts/class_names.json")
METRICS_PATH      = Path("artifacts/metrics.json")
CM_PATH           = Path("artifacts/confusion_matrix.png")
ROC_PATH          = Path("artifacts/roc_curve.png")

for p, label in [(MODEL_PATH, "Model"), (CLASS_NAMES_PATH, "Class names")]:
    if not p.exists():
        st.error(f"{label} file not found: `{p}`")
        st.stop()

try:
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
@st.cache_resource(show_spinner="Loading model…")
def load_model():
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        st.error(f"Model load error: {e}")
        return None

@st.cache_data(show_spinner=False)
def get_class_names():
    return load_class_names(CLASS_NAMES_PATH)

@st.cache_data(show_spinner=False)
def get_metrics():
    if METRICS_PATH.exists():
        return json.loads(METRICS_PATH.read_text())
    return {}

# ── Inference ────────────────────────────────────────────────────────────────
def run_predict(model, class_names, image: "Image.Image"):
    img = image.convert("RGB").resize((FEATURE_IMAGE_SIZE, FEATURE_IMAGE_SIZE))
    feat = extract_features_from_image(img)
    X = np.expand_dims(feat, axis=0)
    idx = int(model.predict(X)[0])
    probs = model.predict_proba(X)[0]
    return class_names[idx], float(probs[idx]), probs

# ── Load ─────────────────────────────────────────────────────────────────────
model       = load_model()
if model is None:
    st.stop()
class_names = get_class_names()
metrics     = get_metrics()

# ════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-title">🔬 Malaria Cell Detection System</div>
  <div class="hero-sub">
    AI-powered blood smear analysis using classical machine learning
    to detect <em>Plasmodium</em> malaria parasites in red blood cells.
  </div>
  <div>
    <span class="badge">🧬 Classical ML</span>
    <span class="badge">📊 Logistic Regression</span>
    <span class="badge">🩸 Blood Smear Analysis</span>
    <span class="badge">⚡ Real-time Inference</span>
    <span class="badge">🗂 NIH Dataset</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# METRICS
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">📈 Model Performance</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
for col, lbl, key in [
    (c1, "Test Accuracy",  "accuracy"),
    (c2, "Precision",      "precision"),
    (c3, "Recall",         "recall"),
    (c4, "F1-Score",       "f1_score"),
    (c5, "ROC-AUC",        "roc_auc"),
]:
    val = f"{metrics.get(key, 0)*100:.1f}%"
    with col:
        st.markdown(f"""
        <div class="mcard">
          <div class="mcard-val">{val}</div>
          <div class="mcard-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# INFO CARDS
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">🛠️ About This Project</div>', unsafe_allow_html=True)
ia, ib, ic = st.columns(3)

with ia:
    st.markdown("""
    <div class="icard">
      <div class="icard-title">🧠 Feature Extraction</div>
      <ul>
        <li>RGB to grayscale conversion</li>
        <li>Color histograms — 16 bins/channel</li>
        <li>Texture &amp; intensity percentiles</li>
        <li>Logistic Regression classifier</li>
        <li>Softmax probability output</li>
      </ul>
    </div>""", unsafe_allow_html=True)

with ib:
    st.markdown("""
    <div class="icard">
      <div class="icard-title">⚙️ Tech Stack</div>
      <ul>
        <li>Python · NumPy · scikit-learn</li>
        <li>Pillow — image processing</li>
        <li>Joblib — model serialization</li>
        <li>Streamlit — web interface</li>
      </ul>
    </div>""", unsafe_allow_html=True)

with ic:
    st.markdown("""
    <div class="icard">
      <div class="icard-title">📦 Dataset &amp; Split</div>
      <ul>
        <li>Dataset: NIH / Kaggle Cell Images (~27,000 images)</li>
        <li>80 / 10 / 10 train–val–test split</li>
        <li><b style="color:#fc8181;">Parasitized</b> — infected cell</li>
        <li><b style="color:#68d391;">Uninfected</b> — healthy cell</li>
      </ul>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# LIVE ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">🧪 Live Cell Analysis</div>', unsafe_allow_html=True)

left, right = st.columns(2, gap="large")

with left:
    st.markdown('<p class="upload-hint">Upload a microscopic blood smear image. The model extracts handcrafted features and classifies the cell in milliseconds.</p>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload", type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Uploaded cell image", use_container_width=True)
        analyze = st.button("🔍 Analyze Cell", type="primary", use_container_width=True)
    else:
        st.markdown("""
        <div class="drop-zone">
          <div class="drop-icon">🩸</div>
          <div class="drop-text">Drag &amp; drop a cell image here</div>
          <div class="drop-hint">PNG · JPG · JPEG supported</div>
        </div>""", unsafe_allow_html=True)
        analyze = False

with right:
    if uploaded and analyze:
        with st.spinner("Analyzing…"):
            try:
                label, conf, probs = run_predict(model, class_names, image)
                parasitized = label.lower() == "parasitized"
                card_cls  = "res-bad" if parasitized else "res-good"
                icon      = "🦠" if parasitized else "✅"
                color     = "#f87171" if parasitized else "#4ade80"

                st.markdown(f"""
                <div class="{card_cls}">
                  <div class="res-icon">{icon}</div>
                  <div class="res-label" style="color:{color};">{label}</div>
                  <div class="res-conf">Confidence: {conf:.1%}</div>
                </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Probability breakdown:**")
                for name, p in zip(class_names, probs):
                    st.caption(name)
                    st.progress(float(p))
                    st.caption(f"{float(p):.2%}")

            except Exception as e:
                st.error(f"Prediction error: {e}")

    elif uploaded and not analyze:
        st.markdown("""
        <div class="await-box">
          <div class="await-icon">👆</div>
          <div class="await-text">Click <b>Analyze Cell</b> to run prediction</div>
        </div>""", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="await-box">
          <div class="await-icon">📊</div>
          <div class="await-text">Awaiting Analysis</div>
          <div class="await-hint">Upload an image and click Analyze</div>
        </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# EVALUATION ARTIFACTS
# ════════════════════════════════════════════════════════════════════════════
if CM_PATH.exists() or ROC_PATH.exists():
    st.markdown('<div class="sec-title">📉 Evaluation Artifacts</div>', unsafe_allow_html=True)
    e1, e2 = st.columns(2)
    if CM_PATH.exists():
        with e1:
            st.image(str(CM_PATH), caption="Confusion Matrix", use_container_width=True)
    if ROC_PATH.exists():
        with e2:
            st.image(str(ROC_PATH), caption="ROC Curve", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
  Built with Python · scikit-learn · Streamlit &nbsp;·&nbsp;
  NIH Cell Images Dataset &nbsp;·&nbsp; Classical ML — no deep learning
</div>
""", unsafe_allow_html=True)
