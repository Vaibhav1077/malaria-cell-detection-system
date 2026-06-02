from __future__ import annotations

import csv
import json
import os
import struct
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "presentation"
PPTX_PATH = OUT_DIR / "Malaria_Detection_Presentation.pptx"
NOTES_PATH = OUT_DIR / "speaker_notes.md"

SLIDE_W = 12192000
SLIDE_H = 6858000

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"


def emu(inches: float) -> int:
    return int(inches * 914400)


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        header = f.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        return 900, 600
    return struct.unpack(">II", header[16:24])


def image_box(path: Path, x: float, y: float, max_w: float, max_h: float) -> tuple[int, int, int, int]:
    width, height = png_size(path)
    ratio = min(max_w / width, max_h / height)
    w = width * ratio
    h = height * ratio
    return emu(x + (max_w - w) / 2), emu(y + (max_h - h) / 2), emu(w), emu(h)


def text_shape(shape_id: int, x: float, y: float, w: float, h: float, text: str, font_size: int = 24,
               bold: bool = False, color: str = "253047") -> str:
    runs = []
    for line in text.split("\n"):
        runs.append(
            f"""
            <a:p>
              <a:r>
                <a:rPr lang="en-US" sz="{font_size * 100}" b="{1 if bold else 0}">
                  <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
                </a:rPr>
                <a:t>{escape(line)}</a:t>
              </a:r>
            </a:p>"""
        )
    return f"""
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="{shape_id}" name="TextBox {shape_id}"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="{emu(x)}" y="{emu(y)}"/>
            <a:ext cx="{emu(w)}" cy="{emu(h)}"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square" anchor="t"/>
          <a:lstStyle/>
          {''.join(runs)}
        </p:txBody>
      </p:sp>"""


def rect_shape(shape_id: int, x: float, y: float, w: float, h: float, fill: str, line: str = "FFFFFF") -> str:
    return f"""
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="{shape_id}" name="Rectangle {shape_id}"/>
          <p:cNvSpPr/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="{emu(x)}" y="{emu(y)}"/>
            <a:ext cx="{emu(w)}" cy="{emu(h)}"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>
          <a:ln><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>
        </p:spPr>
      </p:sp>"""


def image_pic(shape_id: int, rid: str, path: Path, x: float, y: float, max_w: float, max_h: float) -> str:
    off_x, off_y, ext_x, ext_y = image_box(path, x, y, max_w, max_h)
    return f"""
      <p:pic>
        <p:nvPicPr>
          <p:cNvPr id="{shape_id}" name="{escape(path.name)}"/>
          <p:cNvPicPr/>
          <p:nvPr/>
        </p:nvPicPr>
        <p:blipFill>
          <a:blip r:embed="{rid}"/>
          <a:stretch><a:fillRect/></a:stretch>
        </p:blipFill>
        <p:spPr>
          <a:xfrm>
            <a:off x="{off_x}" y="{off_y}"/>
            <a:ext cx="{ext_x}" cy="{ext_y}"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        </p:spPr>
      </p:pic>"""


def slide_xml(title: str, body_shapes: list[str], slide_no: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}">
  <p:cSld>
    <p:bg>
      <p:bgPr>
        <a:solidFill><a:srgbClr val="F7F9FB"/></a:solidFill>
        <a:effectLst/>
      </p:bgPr>
    </p:bg>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      {rect_shape(2, 0, 0, 13.333, 0.26, "2A9D8F", "2A9D8F")}
      {text_shape(3, 0.62, 0.48, 11.8, 0.62, title, 30, True, "16324F")}
      {''.join(body_shapes)}
      {text_shape(90, 12.35, 7.05, 0.6, 0.25, str(slide_no), 9, False, "6C757D")}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def rels_xml(rels: list[tuple[str, str, str]]) -> str:
    items = []
    for rid, typ, target in rels:
        items.append(f'<Relationship Id="{rid}" Type="{typ}" Target="{escape(target)}"/>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(items)
        + "</Relationships>"
    )


def bullet_block(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def load_metrics() -> dict[str, float]:
    with (ROOT / "artifacts" / "metrics.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def load_report_rows() -> list[dict[str, str]]:
    path = ROOT / "artifacts" / "classification_report.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_sample(class_name: str) -> Path | None:
    folder = ROOT / "data" / "cell_images" / class_name
    for ext in ("*.png", "*.jpg", "*.jpeg"):
        match = next(folder.glob(ext), None)
        if match:
            return match
    return None


def make_slides() -> tuple[list[dict], list[Path]]:
    metrics = load_metrics()
    parasitized = find_sample("Parasitized")
    uninfected = find_sample("Uninfected")
    confusion = ROOT / "artifacts" / "confusion_matrix.png"
    roc = ROOT / "artifacts" / "roc_curve.png"
    images = [p for p in [parasitized, uninfected, confusion, roc] if p and p.exists()]

    metric_text = "\n".join(
        [
            f"Validation Accuracy: {metrics['validation_accuracy'] * 100:.2f}%",
            f"Test Accuracy: {metrics['accuracy'] * 100:.2f}%",
            f"Precision: {metrics['precision'] * 100:.2f}%",
            f"Recall: {metrics['recall'] * 100:.2f}%",
            f"F1-score: {metrics['f1_score'] * 100:.2f}%",
            f"ROC-AUC: {metrics['roc_auc'] * 100:.2f}%",
        ]
    )

    slides = [
        {
            "title": "Malaria Detection Using Machine Learning",
            "shapes": [
                text_shape(10, 0.75, 1.65, 7.2, 1.5, "Classical ML based classification of blood smear cell images", 28, True, "253047"),
                text_shape(11, 0.78, 3.0, 6.7, 1.8, "Classes: Parasitized and Uninfected\nApproach: handcrafted image features with traditional ML models\nDemo: Streamlit web application", 20),
                rect_shape(12, 8.2, 1.25, 4.4, 4.75, "EAF4F4", "B8D8D8"),
                text_shape(13, 8.65, 2.0, 3.6, 2.7, "A lightweight, explainable pipeline for academic learning and presentation.", 26, True, "16324F"),
            ],
            "notes": "Introduce the topic and say the project predicts whether a blood cell image is infected or healthy using classical machine learning.",
        },
        {
            "title": "Problem Statement",
            "shapes": [
                text_shape(10, 0.8, 1.35, 11.5, 3.4, bullet_block([
                    "Manual malaria diagnosis depends on microscopic blood smear examination.",
                    "It requires trained medical experts and takes time.",
                    "Rural or resource-limited areas may not have quick access to specialists.",
                    "Goal: classify a cell image as Parasitized or Uninfected."
                ]), 22),
            ],
            "notes": "Explain why automation can help: it is faster, scalable, and can support screening, though it is not a replacement for doctors.",
        },
        {
            "title": "Objectives",
            "shapes": [
                text_shape(10, 0.8, 1.25, 11.6, 4.2, bullet_block([
                    "Build an end-to-end classical ML pipeline.",
                    "Extract useful handcrafted image features.",
                    "Train Logistic Regression, SVM, and Random Forest classifiers.",
                    "Evaluate using accuracy, precision, recall, F1-score, ROC-AUC, confusion matrix, and ROC curve.",
                    "Provide a Streamlit interface for image upload and prediction."
                ]), 22),
            ],
            "notes": "Keep this slide crisp. These are the project deliverables and evaluation goals.",
        },
        {
            "title": "Dataset",
            "shapes": [
                text_shape(10, 0.75, 1.2, 5.5, 1.7, "NIH Malaria Cell Images Dataset or similar two-class cell image dataset.", 22),
                text_shape(11, 0.75, 2.85, 5.5, 1.5, "Folder structure:\ndata/cell_images/Parasitized\ndata/cell_images/Uninfected", 19, False, "253047"),
                *( [image_pic(12, "rId2", parasitized, 6.75, 1.35, 2.6, 2.6),
                    text_shape(13, 6.9, 4.05, 2.3, 0.35, "Parasitized", 16, True, "A23E48")] if parasitized else [] ),
                *( [image_pic(14, "rId3", uninfected, 9.7, 1.35, 2.6, 2.6),
                    text_shape(15, 9.95, 4.05, 2.1, 0.35, "Uninfected", 16, True, "2A9D8F")] if uninfected else [] ),
            ],
            "notes": "Mention that the dataset has two labeled folders. Each image represents a single blood cell.",
            "images": [p for p in [parasitized, uninfected] if p],
        },
        {
            "title": "Proposed System Workflow",
            "shapes": [
                text_shape(10, 0.72, 1.22, 12.0, 4.9, "1. Load images from dataset folders\n2. Resize each image to 32 x 32 pixels\n3. Extract handcrafted feature vectors\n4. Split data into train, validation, and test sets\n5. Train ML classifier\n6. Evaluate model performance\n7. Save model and use it for predictions", 22),
            ],
            "notes": "Walk through the pipeline from raw images to final prediction. This is the core methodology.",
        },
        {
            "title": "Feature Extraction",
            "shapes": [
                text_shape(10, 0.8, 1.3, 11.5, 4.3, bullet_block([
                    "Grayscale pixel values from resized images.",
                    "RGB channel mean and standard deviation.",
                    "Color histogram features.",
                    "Basic texture statistics: mean, standard deviation, and percentiles.",
                    "All features are combined into one numeric vector."
                ]), 22),
            ],
            "notes": "Highlight that this project does not use CNN or deep learning. It converts each image into numeric handcrafted features.",
        },
        {
            "title": "Algorithms Used",
            "shapes": [
                text_shape(10, 0.85, 1.3, 3.4, 3.8, "Logistic Regression\n\nSimple linear baseline model. Current saved model uses this classifier.", 20),
                text_shape(11, 4.95, 1.3, 3.4, 3.8, "Support Vector Machine\n\nStrong classical classifier for high-dimensional feature vectors.", 20),
                text_shape(12, 9.05, 1.3, 3.4, 3.8, "Random Forest\n\nTree-based ensemble model that can capture non-linear feature patterns.", 20),
            ],
            "notes": "Explain that multiple classical models are supported. The current metrics come from the saved Logistic Regression model.",
        },
        {
            "title": "Implementation",
            "shapes": [
                text_shape(10, 0.78, 1.25, 5.7, 4.2, bullet_block([
                    "Python for programming.",
                    "Pillow for image loading and resizing.",
                    "NumPy and Pandas for data handling.",
                    "Scikit-learn for ML models and metrics.",
                    "Matplotlib and Seaborn for plots.",
                    "Joblib for saving trained model.",
                    "Streamlit for web app demo."
                ]), 20),
                text_shape(11, 7.0, 1.45, 4.9, 3.2, "Main files:\ntrain.py\npredict.py\napp.py\nsrc/data.py\nsrc/model.py\nsrc/evaluate.py", 22, True, "16324F"),
            ],
            "notes": "Mention the important libraries and files. This helps during viva when they ask how it is implemented.",
        },
        {
            "title": "Model Performance",
            "shapes": [
                rect_shape(10, 0.85, 1.25, 5.4, 4.75, "FFFFFF", "D9E2EC"),
                text_shape(11, 1.25, 1.62, 4.5, 3.6, metric_text, 22, True, "253047"),
                text_shape(12, 7.0, 1.45, 4.9, 3.8, "Recall is higher than precision, so the model is comparatively better at finding infected cells than avoiding false positives.\n\nROC-AUC around 86.94% shows good class separation for a classical ML model.", 21),
            ],
            "notes": "Present the numbers clearly. Accuracy is about 80 percent and ROC-AUC is about 87 percent.",
        },
        {
            "title": "Confusion Matrix",
            "shapes": [
                image_pic(10, "rId2", confusion, 0.95, 1.05, 6.2, 5.55),
                text_shape(11, 7.65, 1.45, 4.7, 3.5, "Confusion matrix compares actual classes with predicted classes.\n\nIt helps identify false positives and false negatives, which are important in medical screening tasks.", 22),
            ],
            "notes": "Explain that the confusion matrix shows where the model is correct and where it makes mistakes.",
            "images": [confusion],
        },
        {
            "title": "ROC Curve",
            "shapes": [
                image_pic(10, "rId2", roc, 0.95, 1.05, 6.2, 5.55),
                text_shape(11, 7.65, 1.45, 4.7, 3.5, "ROC curve shows the trade-off between true positive rate and false positive rate.\n\nA higher ROC-AUC means the classifier separates infected and healthy cells better.", 22),
            ],
            "notes": "Say that the ROC-AUC value is 86.94 percent, which is a strong result for a handcrafted-feature approach.",
            "images": [roc],
        },
        {
            "title": "Web Application Demo",
            "shapes": [
                text_shape(10, 0.82, 1.28, 11.3, 4.2, bullet_block([
                    "Built using Streamlit.",
                    "User uploads a blood smear cell image.",
                    "Saved model predicts Parasitized or Uninfected.",
                    "App displays predicted class, confidence, and class probabilities.",
                    "Built-in demo samples are available for smooth presentation."
                ]), 22),
                text_shape(11, 0.92, 5.65, 10.8, 0.5, "Run command: streamlit run app.py", 20, True, "2A9D8F"),
            ],
            "notes": "At this slide, switch to the live Streamlit app if you want to show the demo.",
        },
        {
            "title": "Advantages, Limitations, and Future Scope",
            "shapes": [
                text_shape(10, 0.75, 1.18, 3.8, 4.8, "Advantages\n- No GPU required\n- Lightweight and explainable\n- Good for academic ML workflow\n- Simple Streamlit deployment", 18, False, "253047"),
                text_shape(11, 4.85, 1.18, 3.8, 4.8, "Limitations\n- Lower accuracy than CNN models\n- Depends on image quality\n- Handcrafted features may miss complex patterns\n- Not for real diagnosis without expert validation", 18, False, "253047"),
                text_shape(12, 8.95, 1.18, 3.8, 4.8, "Future Scope\n- Add HOG or LBP features\n- Add cross-validation\n- Compare more models\n- Improve UI and deploy online", 18, False, "253047"),
            ],
            "notes": "Conclude honestly: the project is educational and useful, but medical use needs stronger validation.",
        },
    ]
    return slides, images


def content_types(slide_count: int, image_count: int) -> str:
    overrides = [
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ]
    for idx in range(1, slide_count + 1):
        overrides.append(
            f'<Override PartName="/ppt/slides/slide{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  {''.join(overrides)}
</Types>"""


def presentation_xml(slide_count: int) -> str:
    slide_ids = []
    for idx in range(1, slide_count + 1):
        slide_ids.append(f'<p:sldId id="{255 + idx}" r:id="rId{idx + 1}"/>')
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>{''.join(slide_ids)}</p:sldIdLst>
  <p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""


def master_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>"""


def layout_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}" type="blank" preserve="1">
  <p:cSld name="Blank">
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""


def theme_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="{NS_A}" name="Malaria Theme">
  <a:themeElements>
    <a:clrScheme name="Office">
      <a:dk1><a:srgbClr val="000000"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="1F2933"/></a:dk2><a:lt2><a:srgbClr val="F7F9FB"/></a:lt2>
      <a:accent1><a:srgbClr val="2A9D8F"/></a:accent1><a:accent2><a:srgbClr val="E76F51"/></a:accent2>
      <a:accent3><a:srgbClr val="16324F"/></a:accent3><a:accent4><a:srgbClr val="F4A261"/></a:accent4>
      <a:accent5><a:srgbClr val="6C757D"/></a:accent5><a:accent6><a:srgbClr val="A23E48"/></a:accent6>
      <a:hlink><a:srgbClr val="0563C1"/></a:hlink><a:folHlink><a:srgbClr val="954F72"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Office"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="Office"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme>
  </a:themeElements>
</a:theme>"""


def write_notes(slides: list[dict]) -> None:
    lines = ["# Malaria Detection Using Machine Learning - Speaker Notes", ""]
    for idx, slide in enumerate(slides, 1):
        lines.extend([f"## Slide {idx}: {slide['title']}", slide["notes"], ""])
    NOTES_PATH.write_text("\n".join(lines), encoding="utf-8")


def build_pptx() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    slides, _ = make_slides()
    image_index: dict[Path, str] = {}
    next_img = 1

    with zipfile.ZipFile(PPTX_PATH, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types(len(slides), 0))
        z.writestr("_rels/.rels", rels_xml([
            ("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument", "ppt/presentation.xml"),
            ("rId2", "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties", "docProps/core.xml"),
            ("rId3", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties", "docProps/app.xml"),
        ]))
        now = datetime.now(timezone.utc).isoformat()
        z.writestr("docProps/core.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Malaria Detection Using Machine Learning</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>""")
        z.writestr("docProps/app.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft PowerPoint</Application><PresentationFormat>On-screen Show (16:9)</PresentationFormat><Slides>{len(slides)}</Slides>
</Properties>""")
        z.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        pres_rels = [("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster", "slideMasters/slideMaster1.xml")]
        for idx in range(1, len(slides) + 1):
            pres_rels.append((f"rId{idx + 1}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide", f"slides/slide{idx}.xml"))
        z.writestr("ppt/_rels/presentation.xml.rels", rels_xml(pres_rels))
        z.writestr("ppt/slideMasters/slideMaster1.xml", master_xml())
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", rels_xml([
            ("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout", "../slideLayouts/slideLayout1.xml"),
            ("rId2", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme", "../theme/theme1.xml"),
        ]))
        z.writestr("ppt/slideLayouts/slideLayout1.xml", layout_xml())
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", rels_xml([
            ("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster", "../slideMasters/slideMaster1.xml"),
        ]))
        z.writestr("ppt/theme/theme1.xml", theme_xml())

        for idx, slide in enumerate(slides, 1):
            z.writestr(f"ppt/slides/slide{idx}.xml", slide_xml(slide["title"], slide["shapes"], idx))
            slide_rels = [("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout", "../slideLayouts/slideLayout1.xml")]
            for img_no, img in enumerate(slide.get("images", []), 2):
                img = Path(img)
                if img not in image_index:
                    media_name = f"image{next_img}{img.suffix.lower()}"
                    image_index[img] = media_name
                    z.write(img, f"ppt/media/{media_name}")
                    next_img += 1
                slide_rels.append((f"rId{img_no}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image", f"../media/{image_index[img]}"))
            z.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", rels_xml(slide_rels))

    write_notes(slides)


if __name__ == "__main__":
    build_pptx()
    print(PPTX_PATH)
    print(NOTES_PATH)
