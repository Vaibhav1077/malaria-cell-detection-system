from __future__ import annotations

import os
from pathlib import Path

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

# ═══════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif !important; }

/* ── Base ── */
.stApp {
    background: #050810;
    color: #e2e8f0;
}
section[data-testid="stSidebar"] { display: none; }
#MainMenu, footer, .stDeployButton { visibility: hidden; }
.block-container { padding: 0 2rem 4rem 2rem !important; max-width: 1200px; }

/* ── Animated gradient top bar ── */
.top-bar {
    height: 4px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899, #f43f5e, #f97316, #eab308, #22c55e, #06b6d4, #6366f1);
    background-size: 300% 100%;
    animation: shimmer 4s linear infinite;
    margin-bottom: 0;
    border-radius: 0 0 8px 8px;
}
@keyframes shimmer { 0%{background-position:0% 0%} 100%{background-position:300% 0%} }

/* ── Hero ── */
.hero-wrap {
    position: relative;
    background: radial-gradient(ellipse at 20% 50%, rgba(99,102,241,0.15) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 20%, rgba(236,72,153,0.12) 0%, transparent 55%),
                radial-gradient(ellipse at 60% 80%, rgba(6,182,212,0.10) 0%, transparent 50%),
                linear-gradient(135deg, #0d1117 0%, #0f172a 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 24px;
    padding: 60px 48px 52px;
    text-align: center;
    margin: 28px 0 40px;
    overflow: hidden;
}
.hero-wrap::before {
    content:'';
    position:absolute; inset:0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%236366f1' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    opacity:.5;
}
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 100px;
    padding: 6px 16px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #818cf8;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 20px;
}
.hero-title {
    font-size: clamp(2rem, 4vw, 3.2rem);
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: -1px;
    margin: 0 0 18px;
    background: linear-gradient(135deg, #ffffff 0%, #c7d2fe 40%, #a5b4fc 70%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1.05rem;
    color: #94a3b8;
    max-width: 560px;
    margin: 0 auto 28px;
    line-height: 1.7;
    font-weight: 400;
}
.badge-row { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }
.badge {
    background: rgba(15,23,42,0.8);
    border: 1px solid rgba(148,163,184,0.15);
    border-radius: 100px;
    padding: 6px 14px;
    font-size: 0.78rem;
    color: #94a3b8;
    font-weight: 500;
}
.badge span { margin-right: 5px; }

/* ── Section title ── */
.sec-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.05rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 40px 0 18px;
}
.sec-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(99,102,241,0.4), transparent);
}

/* ── Metric cards ── */
.metric-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 14px; margin-bottom: 8px; }
.metric-card {
    background: linear-gradient(145deg, #0d1117, #111827);
    border: 1px solid rgba(148,163,184,0.08);
    border-radius: 16px;
    padding: 22px 16px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
}
.metric-card::before {
    content:'';
    position:absolute;
    top:0; left:0; right:0;
    height:3px;
    border-radius:16px 16px 0 0;
}
.mc-blue::before   { background: linear-gradient(90deg,#6366f1,#8b5cf6); }
.mc-pink::before   { background: linear-gradient(90deg,#ec4899,#f43f5e); }
.mc-green::before  { background: linear-gradient(90deg,#10b981,#06b6d4); }
.mc-orange::before { background: linear-gradient(90deg,#f97316,#eab308); }
.mc-cyan::before   { background: linear-gradient(90deg,#06b6d4,#3b82f6); }
.metric-val {
    font-size: 2.1rem;
    font-weight: 800;
    color: #f1f5f9;
    letter-spacing: -1px;
    line-height: 1;
}
.mc-blue   .metric-val { color: #a5b4fc; }
.mc-pink   .metric-val { color: #f9a8d4; }
.mc-green  .metric-val { color: #6ee7b7; }
.mc-orange .metric-val { color: #fed7aa; }
.mc-cyan   .metric-val { color: #a5f3fc; }
.metric-lbl {
    font-size: 0.72rem;
    color: #64748b;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

/* ── Info cards ── */
.info-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; }
.info-card {
    background: linear-gradient(145deg, #0d1117, #111827);
    border: 1px solid rgba(148,163,184,0.08);
    border-radius: 16px;
    padding: 26px 24px;
}
.info-card-head {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.92rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(148,163,184,0.08);
}
.info-icon {
    width: 34px; height: 34px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}
.ic-purple { background: rgba(99,102,241,0.15); }
.ic-blue   { background: rgba(6,182,212,0.15); }
.ic-rose   { background: rgba(244,63,94,0.15); }
.info-list {
    list-style: none;
    padding: 0; margin: 0;
}
.info-list li {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 0.86rem;
    color: #94a3b8;
    padding: 5px 0;
    line-height: 1.5;
}
.info-list li::before {
    content: '›';
    color: #6366f1;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 1px;
}

/* ── Upload zone ── */
.upload-outer {
    background: linear-gradient(145deg, #0d1117, #111827);
    border: 1px solid rgba(148,163,184,0.08);
    border-radius: 20px;
    padding: 28px;
}
.drop-placeholder {
    border: 2px dashed rgba(99,102,241,0.3);
    border-radius: 14px;
    padding: 56px 24px;
    text-align: center;
    background: rgba(99,102,241,0.03);
}
.drop-icon { font-size: 3.2rem; margin-bottom: 12px; }
.drop-text { color: #64748b; font-size: 0.92rem; margin: 4px 0; }
.drop-hint { color: #475569; font-size: 0.78rem; }

/* ── Result panel ── */
.result-outer {
    background: linear-gradient(145deg, #0d1117, #111827);
    border: 1px solid rgba(148,163,184,0.08);
    border-radius: 20px;
    padding: 28px;
    height: 100%;
}
.result-waiting {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 260px;
    color: #334155;
    text-align: center;
    gap: 12px;
}
.result-waiting-icon { font-size: 3rem; opacity: 0.4; }
.result-waiting-text { font-size: 0.9rem; }

.result-card-parasitized {
    background: linear-gradient(135deg, rgba(239,68,68,0.08), rgba(185,28,28,0.05));
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 16px;
    padding: 30px 24px;
    text-align: center;
    margin-bottom: 20px;
}
.result-card-uninfected {
    background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(5,150,105,0.05));
    border: 1px solid rgba(16,185,129,0.25);
    border-radius: 16px;
    padding: 30px 24px;
    text-align: center;
    margin-bottom: 20px;
}
.result-emoji { font-size: 3.5rem; margin-bottom: 8px; }
.result-label-text {
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 4px 0;
}
.result-conf { font-size: 0.9rem; color: #94a3b8; margin-top: 6px; }

/* Probability bars */
.prob-row { margin-bottom: 14px; }
.prob-header {
    display: flex;
    justify-content: space-between;
    font-size: 0.82rem;
    margin-bottom: 6px;
    color: #94a3b8;
    font-weight: 500;
}
.prob-bar-bg {
    background: rgba(148,163,184,0.08);
    border-radius: 100px;
    height: 8px;
    overflow: hidden;
}
.prob-bar-fill {
    height: 100%;
    border-radius: 100px;
    transition: width 0.6s ease;
}
.pb-red   { background: linear-gradient(90deg,#f43f5e,#ec4899); }
.pb-green { background: linear-gradient(90deg,#10b981,#06b6d4); }

/* ── Artifacts ── */
.artifact-card {
    background: linear-gradient(145deg,#0d1117,#111827);
    border: 1px solid rgba(148,163,184,0.08);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
}
.artifact-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 14px;
}

/* ── Footer ── */
.footer-wrap {
    margin-top: 56px;
    padding-top: 24px;
    border-top: 1px solid rgba(148,163,184,0.08);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}
.footer-left { font-size: 0.82rem; color: #334155; }
.footer-left b { color: #475569; }
.footer-right { font-size: 0.78rem; color: #1e293b; }

/* ── Streamlit widget overrides ── */
div[data-testid="stFileUploader"] {
    background: transparent !important;
}
div[data-testid="stFileUploader"] > div {
    background: rgba(99,102,241,0.05) !important;
    border: 1px dashed rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
}
.stButton > button {
    background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 14px 24px !important;
    letter-spacing: 0.3px !important;
    transition: opacity 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover { opacity: 0.88 !important; }
.stSpinner > div { border-top-color: #6366f1 !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  PATHS & IMPORTS
# ═══════════════════════════════════════════════════════════════
MODEL_PATH          = Path("models/malaria_ml.joblib")
CLASS_NAMES_PATH    = Path("artifacts/class_names.json")
METRICS_PATH        = Path("artifacts/metrics.json")
CONFUSION_MATRIX    = Path("artifacts/confusion_matrix.png")
ROC_CURVE           = Path("artifacts/roc_curve.png")

for p, label in [(MODEL_PATH, "Model"), (CLASS_NAMES_PATH, "Class names")]:
    if not p.exists():
        st.error(f"{label} file not found: `{p}`")
        st.stop()

try:
    import json, joblib
    import numpy as np
    from PIL import Image
    from src.config import FEATURE_IMAGE_SIZE
    from src.data import extract_features_from_image
    from src.utils import load_class_names
except Exception as e:
    st.error(f"Import error: {e}")
    st.stop()

# ═══════════════════════════════════════════════════════════════
#  LOADERS
# ═══════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="Loading model…")
def load_model():
    return joblib.load(MODEL_PATH)

@st.cache_data(show_spinner=False)
def get_class_names():
    return load_class_names(CLASS_NAMES_PATH)

@st.cache_data(show_spinner=False)
def get_metrics():
    if METRICS_PATH.exists():
        return json.loads(METRICS_PATH.read_text())
    return {}

model       = load_model()
class_names = get_class_names()
metrics     = get_metrics()

# ═══════════════════════════════════════════════════════════════
#  INFERENCE
# ═══════════════════════════════════════════════════════════════
def run_inference(image: "Image.Image"):
    img = image.convert("RGB").resize((FEATURE_IMAGE_SIZE, FEATURE_IMAGE_SIZE))
    feat = extract_features_from_image(img)
    X = np.expand_dims(feat, 0)
    idx   = int(model.predict(X)[0])
    probs = model.predict_proba(X)[0]
    return class_names[idx], float(probs[idx]), probs

# ═══════════════════════════════════════════════════════════════
#  TOP BAR
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="top-bar"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  HERO
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-wrap">
  <div class="hero-eyebrow">🔬 AI-Powered Medical Imaging</div>
  <h1 class="hero-title">Malaria Cell Detection System</h1>
  <p class="hero-sub">
    Automated detection of <em>Plasmodium</em> parasites in blood smear images
    using handcrafted features and classical machine learning.
  </p>
  <div class="badge-row">
    <div class="badge"><span>🧠</span>Logistic Regression</div>
    <div class="badge"><span>🩸</span>Blood Smear Analysis</div>
    <div class="badge"><span>📊</span>NIH Dataset</div>
    <div class="badge"><span>⚡</span>Real-time Inference</div>
    <div class="badge"><span>🐍</span>scikit-learn · Python</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  METRICS
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">📈 Model Performance</div>', unsafe_allow_html=True)

m = metrics
mc = [
    ("mc-blue",   f"{m.get('accuracy',0)*100:.1f}%",   "Test Accuracy"),
    ("mc-pink",   f"{m.get('precision',0)*100:.1f}%",  "Precision"),
    ("mc-green",  f"{m.get('recall',0)*100:.1f}%",     "Recall"),
    ("mc-orange", f"{m.get('f1_score',0)*100:.1f}%",   "F1-Score"),
    ("mc-cyan",   f"{m.get('roc_auc',0)*100:.1f}%",    "ROC-AUC"),
]
cols = st.columns(5)
for col, (cls, val, lbl) in zip(cols, mc):
    with col:
        st.markdown(f"""
        <div class="metric-card {cls}">
            <div class="metric-val">{val}</div>
            <div class="metric-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  INFO CARDS
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">🛠️ Project Overview</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="info-card">
      <div class="info-card-head">
        <div class="info-icon ic-purple">🧠</div>
        How It Works
      </div>
      <ul class="info-list">
        <li>Image resized to 32 × 32 px</li>
        <li>RGB to grayscale conversion</li>
        <li>Color histograms — 16 bins × 3 channels</li>
        <li>Texture &amp; intensity percentile stats</li>
        <li>Logistic Regression classifier</li>
        <li>Softmax probability output</li>
      </ul>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="info-card">
      <div class="info-card-head">
        <div class="info-icon ic-blue">⚙️</div>
        Tech Stack
      </div>
      <ul class="info-list">
        <li>Python 3.x</li>
        <li>scikit-learn — model training &amp; evaluation</li>
        <li>NumPy — feature computation</li>
        <li>Pillow — image preprocessing</li>
        <li>Joblib — model serialization</li>
        <li>Streamlit — web interface</li>
      </ul>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="info-card">
      <div class="info-card-head">
        <div class="info-icon ic-rose">🩺</div>
        Detection Classes
      </div>
      <ul class="info-list">
        <li><b style="color:#fca5a5;">🔴 Parasitized</b> — Cell infected with <i>Plasmodium</i> falciparum malaria parasite</li>
        <li><b style="color:#6ee7b7;">🟢 Uninfected</b> — Healthy red blood cell with no parasite present</li>
        <li>Dataset: NIH / Kaggle Cell Images (~27,000 images)</li>
        <li>80 / 10 / 10 train–val–test split</li>
      </ul>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  PREDICTION
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">🖼️ Live Cell Analysis</div>', unsafe_allow_html=True)

left, right = st.columns([1, 1], gap="large")

# ── LEFT: uploader ──
with left:
    st.markdown('<div class="upload-outer">', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.88rem;color:#64748b;margin:0 0 14px;">
        Upload a microscopic blood smear image. The model extracts handcrafted
        features and classifies the cell in milliseconds.
    </p>""", unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload cell image",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
    )

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        analyze = st.button("🔍  Analyze Cell", type="primary")
    else:
        st.markdown("""
        <div class="drop-placeholder">
            <div class="drop-icon">🩸</div>
            <div class="drop-text">Drag &amp; drop a cell image here</div>
            <div class="drop-hint">PNG · JPG · JPEG supported</div>
        </div>""", unsafe_allow_html=True)
        analyze = False

    st.markdown('</div>', unsafe_allow_html=True)

# ── RIGHT: results ──
with right:
    st.markdown('<div class="result-outer">', unsafe_allow_html=True)

    if not uploaded:
        st.markdown("""
        <div class="result-waiting">
            <div class="result-waiting-icon">📊</div>
            <div class="result-waiting-text" style="color:#475569;font-size:1rem;font-weight:600;">
                Awaiting Analysis
            </div>
            <div style="color:#334155;font-size:0.83rem;">
                Upload an image and click Analyze
            </div>
        </div>""", unsafe_allow_html=True)

    elif uploaded and not analyze:
        st.markdown("""
        <div class="result-waiting">
            <div class="result-waiting-icon">👆</div>
            <div class="result-waiting-text" style="color:#6366f1;font-size:1rem;font-weight:600;">
                Ready to Analyze
            </div>
            <div style="color:#475569;font-size:0.83rem;">
                Click the <b>Analyze Cell</b> button
            </div>
        </div>""", unsafe_allow_html=True)

    else:
        with st.spinner("Analyzing cell…"):
            try:
                label, confidence, probs = run_inference(image)
                is_para = label.lower() == "parasitized"

                card_cls   = "result-card-parasitized" if is_para else "result-card-uninfected"
                emoji      = "🦠" if is_para else "✅"
                lbl_color  = "#fca5a5" if is_para else "#6ee7b7"
                status_txt = "Parasite Detected" if is_para else "No Parasite Found"

                st.markdown(f"""
                <div class="{card_cls}">
                    <div class="result-emoji">{emoji}</div>
                    <div class="result-label-text" style="color:{lbl_color};">{label}</div>
                    <div style="font-size:0.85rem;color:#64748b;margin-top:4px;">{status_txt}</div>
                    <div class="result-conf">Confidence: <b style="color:{lbl_color};">{confidence:.1%}</b></div>
                </div>""", unsafe_allow_html=True)

                # Probability bars
                st.markdown("""
                <div style="font-size:0.82rem;font-weight:600;color:#64748b;
                            text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">
                    Probability Breakdown
                </div>""", unsafe_allow_html=True)

                bar_colors = {"parasitized": "pb-red", "uninfected": "pb-green"}
                for name, prob in zip(class_names, probs):
                    pct  = f"{float(prob)*100:.1f}%"
                    bcls = bar_colors.get(name.lower(), "pb-green")
                    w    = int(float(prob) * 100)
                    st.markdown(f"""
                    <div class="prob-row">
                        <div class="prob-header">
                            <span>{name}</span><span>{pct}</span>
                        </div>
                        <div class="prob-bar-bg">
                            <div class="prob-bar-fill {bcls}" style="width:{w}%"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)

                # Advisory
                advisory_bg  = "rgba(239,68,68,0.06)"  if is_para else "rgba(16,185,129,0.06)"
                advisory_bdr = "rgba(239,68,68,0.2)"   if is_para else "rgba(16,185,129,0.2)"
                advisory_msg = (
                    "⚠️ Possible infection detected. Please consult a medical professional for confirmation."
                    if is_para else
                    "✅ Cell appears healthy. This is an automated prediction — always confirm clinically."
                )
                st.markdown(f"""
                <div style="background:{advisory_bg};border:1px solid {advisory_bdr};
                            border-radius:10px;padding:12px 16px;margin-top:16px;
                            font-size:0.82rem;color:#94a3b8;line-height:1.6;">
                    {advisory_msg}
                </div>""", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Prediction error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  EVALUATION ARTIFACTS
# ═══════════════════════════════════════════════════════════════
if CONFUSION_MATRIX.exists() or ROC_CURVE.exists():
    st.markdown('<div class="sec-title">📉 Evaluation Artifacts</div>', unsafe_allow_html=True)
    ac1, ac2 = st.columns(2)
    if CONFUSION_MATRIX.exists():
        with ac1:
            st.markdown('<div class="artifact-card">', unsafe_allow_html=True)
            st.markdown('<div class="artifact-title">Confusion Matrix</div>', unsafe_allow_html=True)
            st.image(str(CONFUSION_MATRIX), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    if ROC_CURVE.exists():
        with ac2:
            st.markdown('<div class="artifact-card">', unsafe_allow_html=True)
            st.markdown('<div class="artifact-title">ROC Curve</div>', unsafe_allow_html=True)
            st.image(str(ROC_CURVE), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer-wrap">
    <div class="footer-left">
        Built with <b>Python</b> · <b>scikit-learn</b> · <b>Streamlit</b>
        &nbsp;·&nbsp; Dataset: NIH Cell Images for Detecting Malaria
    </div>
    <div class="footer-right">
        Classical ML &nbsp;·&nbsp; No deep learning &nbsp;·&nbsp; Open Source
    </div>
</div>
""", unsafe_allow_html=True)
