# Malaria Detection Using Machine Learning

## 1. Title

Malaria Detection Using Machine Learning

## 2. Abstract

Malaria is a serious infectious disease caused by Plasmodium parasites and transmitted through infected female Anopheles mosquitoes. Manual diagnosis usually depends on microscopic examination of blood smear images, which requires trained medical experts and can be time-consuming. This project presents a classical Machine Learning based system for identifying whether a red blood cell image is Parasitized or Uninfected. Instead of using Deep Learning, the project extracts handcrafted features from blood smear images and trains traditional ML classifiers such as Support Vector Machine, Random Forest, and Logistic Regression.

## 3. Problem Statement

Manual malaria detection is slow, skill-dependent, and difficult to scale in rural or resource-limited areas. The goal of this project is to build a simple ML model that can classify blood cell images into two categories: Parasitized and Uninfected.

## 4. Objectives

- Build a classical Machine Learning pipeline for malaria cell classification.
- Extract useful image features from blood smear cell images.
- Train ML classifiers such as SVM, Random Forest, and Logistic Regression.
- Evaluate model performance using accuracy, precision, recall, F1-score, ROC-AUC, confusion matrix, and ROC curve.
- Provide a simple Streamlit interface where users can upload an image and get prediction output.

## 5. Dataset

The project expects the NIH Malaria Cell Images Dataset or any similar dataset with two classes:

- Parasitized: infected cell images.
- Uninfected: healthy cell images.

Expected folder structure:

```text
data/
  cell_images/
    Parasitized/
      image1.png
      image2.png
    Uninfected/
      image1.png
      image2.png
```

## 6. Proposed System

The proposed system follows a classical ML workflow:

1. Load images from dataset folders.
2. Resize each image to 32x32 pixels.
3. Extract handcrafted features.
4. Split data into training, validation, and testing sets.
5. Train a Machine Learning classifier.
6. Evaluate model performance.
7. Save trained model and reports.
8. Use the saved model for image prediction.

## 7. Feature Extraction

This project does not use CNN or Deep Learning. It uses handcrafted image features:

- Grayscale pixel values from resized image.
- RGB channel mean values.
- RGB channel standard deviation values.
- Color histogram features.
- Basic texture statistics such as mean, standard deviation, and percentiles.

These features are combined into a numeric feature vector and passed to a classical ML classifier.

## 8. Machine Learning Algorithms

The project supports three ML classifiers:

- Support Vector Machine: default and recommended classifier.
- Random Forest: tree-based ensemble classifier.
- Logistic Regression: simple linear baseline classifier.

The default training command uses SVM:

```powershell
python train.py --data-dir data/cell_images --model-type svm
```

## 9. Implementation Details

Programming language: Python

Main libraries:

- NumPy for numerical operations.
- Pandas for saving reports.
- Pillow for image loading and resizing.
- Scikit-learn for ML models, splitting, and evaluation metrics.
- Matplotlib and Seaborn for plots.
- Joblib for saving trained model.
- Streamlit for web interface.

## 10. Project Files

- train.py: trains the ML model and saves reports.
- predict.py: predicts class for a single image.
- app.py: Streamlit web app for image upload and prediction.
- requirements.txt: required Python packages.
- README.md: setup and usage instructions.
- src/config.py: project configuration.
- src/data.py: image loading and feature extraction.
- src/model.py: ML model selection.
- src/evaluate.py: evaluation metrics and graphs.
- src/utils.py: helper functions.

## 11. Training Process

To train the model:

```powershell
cd malaria-cell-detection-system
.venv\Scripts\activate
python train.py --data-dir data/cell_images --model-type svm
```

After training, the following outputs are generated:

- models/malaria_ml.joblib
- artifacts/class_names.json
- artifacts/metrics.json
- artifacts/classification_report.csv
- artifacts/confusion_matrix.png
- artifacts/roc_curve.png

## 12. Prediction Process

To predict a single image:

```powershell
python predict.py --image "path\to\image.png" --model models/malaria_ml.joblib --class-names artifacts/class_names.json
```

The output shows:

- Predicted class.
- Confidence score.
- Probability of each class.

## 13. Web Application

The project includes a Streamlit app. It allows the user to upload a blood smear image and displays the prediction result.

Run command:

```powershell
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## 14. Evaluation Metrics

The model is evaluated using:

- Accuracy: overall correct predictions.
- Precision: correctness of positive predictions.
- Recall: ability to detect positive class.
- F1-score: balance between precision and recall.
- ROC-AUC: classification quality across thresholds.
- Confusion matrix: actual vs predicted class comparison.

## 15. Advantages

- Does not require GPU.
- Faster and lighter than Deep Learning models.
- Easier to explain in college presentation or viva.
- Uses classical Machine Learning concepts.
- Simple deployment through Streamlit.

## 16. Limitations

- Accuracy may be lower than advanced CNN models.
- Handcrafted features may not capture all complex image patterns.
- Performance depends on dataset quality and image clarity.
- Not intended for real medical diagnosis without expert validation.

## 17. Future Scope

- Add more feature extraction techniques such as HOG or LBP.
- Add model comparison table.
- Add cross-validation.
- Improve UI with result history.
- Deploy web app online.

## 18. Conclusion

This project demonstrates a classical Machine Learning approach for malaria detection from blood smear cell images. It avoids Deep Learning and uses handcrafted image features with ML classifiers. The system provides training, evaluation, prediction, and a simple web interface, making it suitable for academic presentation and learning core ML workflow.
