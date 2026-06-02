# Malaria Detection Using Machine Learning

This project implements an end-to-end malaria cell image classification system using classical Machine Learning. It classifies blood smear cell images as `Parasitized` or `Uninfected` using handcrafted image features and traditional classifiers such as Logistic Regression, SVM, and Random Forest.

---

## Features

* Classical ML pipeline using handcrafted image features
* Automatic train/validation/test split
* Metrics: accuracy, precision, recall, F1-score, ROC-AUC
* Confusion matrix and ROC curve export
* CLI prediction for single images
* Streamlit web app for demo/presentation

---

## Current Trained Model

The current saved model was trained with:

```
Model: Logistic Regression
Dataset: data/cell_images
Classes: Parasitized, Uninfected
Split: 80% train, 10% validation, 10% test
```

### Evaluation Metrics

```
Validation Accuracy: 81.13%
Test Accuracy:       79.57%
Precision:           77.52%
Recall:              83.31%
F1-score:            80.31%
ROC-AUC:             86.94%
```

---

## Dataset Structure

Make sure your dataset is placed in the following structure:

```
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

Expected path:

```
C:\Users\iamva\OneDrive\Documents\New project\data\cell_images
```

---

## How To Run (Presentation)

### 1. Navigate to project folder

```bash
cd "C:\Users\iamva\OneDrive\Documents\New project"
```

### 2. Activate virtual environment

```bash
.\.venv\Scripts\activate
```

### 3. Run Streamlit app

```bash
streamlit run app.py
```

If the above command does not work:

```bash
python -m streamlit run app.py
```

### 4. Open in browser

```
http://localhost:8501
```

---

## Demo Usage

For a smooth presentation, use built-in demo samples available in the Streamlit app:

* `Parasitized demo sample`
* `Uninfected demo sample`

These samples are pre-tested with the trained model.

---

## Fresh Setup On Another System

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Train The Model (Optional)

Training is already completed. Run only if you want to retrain:

```bash
python train.py --data-dir data/cell_images --model-type logistic_regression
```

Other models:

```bash
python train.py --data-dir data/cell_images --model-type svm
python train.py --data-dir data/cell_images --model-type random_forest
```

Outputs generated:

* artifacts/class_names.json
* artifacts/metrics.json
* artifacts/classification_report.csv
* artifacts/confusion_matrix.png
* artifacts/roc_curve.png
* models/malaria_ml.joblib

---

## Predict On Single Image

```bash
python predict.py --image path/to/image.png --model models/malaria_ml.joblib --class-names artifacts/class_names.json
```

Example:

```bash
python predict.py --image "data/cell_images/Parasitized/sample.png" --model models/malaria_ml.joblib --class-names artifacts/class_names.json
```

---

## Run Web App

```bash
streamlit run app.py
```

Then open:

```
http://localhost:8501
```

---

## Project Structure

```
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

---

## Notes

* This is a classical Machine Learning model, not a deep learning model
* Accuracy is around 80%, so some misclassifications are expected
* Use demo samples for best presentation results

---

## Common Issues

**Streamlit not updating:**

```
Ctrl + C
streamlit run app.py
```

**Browser not refreshing:**

```
Ctrl + F5
```

**Streamlit not recognized:**

```
python -m streamlit run app.py
```
