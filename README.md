# Malaria Cell Detection System

Classical machine learning project for classifying blood smear cell images as `Parasitized` or `Uninfected`.

The repository includes the application code, training pipeline, saved model, and evaluation artifacts. The dataset is not included because it is large; download it separately and place it in the folder structure shown below.

## Features

* Handcrafted image feature extraction
* Logistic Regression, SVM, and Random Forest training options
* Train/validation/test split
* Accuracy, precision, recall, F1-score, ROC-AUC reports
* Confusion matrix and ROC curve output
* Single-image CLI prediction
* Streamlit web app

## Project Structure

```text
.
|-- app.py
|-- train.py
|-- predict.py
|-- requirements.txt
|-- README.md
|-- models/
|   |-- malaria_ml.joblib
|-- artifacts/
|   |-- class_names.json
|   |-- metrics.json
|   |-- classification_report.csv
|   |-- confusion_matrix.png
|   |-- roc_curve.png
|-- data/
|   |-- cell_images/
|       |-- Parasitized/
|       |-- Uninfected/
|-- src/
|   |-- config.py
|   |-- data.py
|   |-- model.py
|   |-- evaluate.py
|   |-- utils.py
```

## Setup

Clone the repository:

```bash
git clone https://github.com/Vaibhav1077/malaria-cell-detection-system.git
cd malaria-cell-detection-system
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.\.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run The Web App

The repository includes a trained model at `models/malaria_ml.joblib`, so the web app can run after dependency installation:

```bash
streamlit run app.py
```

If `streamlit` is not recognized:

```bash
python -m streamlit run app.py
```

Open this URL in your browser:

```text
http://localhost:8501
```

Upload a blood smear image to get a prediction.

## Dataset

To retrain the model or use the built-in demo samples, download the malaria cell image dataset and place it like this:

```text
data/
  cell_images/
    Parasitized/
      image1.png
      image2.png
      ...
    Uninfected/
      image1.png
      image2.png
      ...
```

Recommended dataset: NIH/Kaggle Cell Images for Detecting Malaria.

The default training command expects this relative path:

```text
data/cell_images
```

## Train The Model

```bash
python train.py --data-dir data/cell_images --model-type logistic_regression
```

Other model options:

```bash
python train.py --data-dir data/cell_images --model-type svm
python train.py --data-dir data/cell_images --model-type random_forest
```

Training outputs are saved to:

```text
models/malaria_ml.joblib
artifacts/
```

## Predict From Command Line

```bash
python predict.py --image path/to/image.png --model models/malaria_ml.joblib --class-names artifacts/class_names.json
```

Example:

```bash
python predict.py --image data/cell_images/Parasitized/sample.png --model models/malaria_ml.joblib --class-names artifacts/class_names.json
```

## Current Model Metrics

```text
Validation Accuracy: 81.13%
Test Accuracy:       79.57%
Precision:           77.52%
Recall:              83.31%
F1-score:            80.31%
ROC-AUC:             86.94%
```

## Notes

* This project uses classical machine learning, not deep learning.
* The dataset is intentionally not committed to GitHub because of its size.
* If you retrain the model, generated files in `models/` and `artifacts/` will be updated locally.
