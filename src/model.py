from __future__ import annotations

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.config import TrainConfig


def build_model(config: TrainConfig):
    if config.model_type == "svm":
        return Pipeline(
            [
                ("scaler", StandardScaler()),
                ("pca", PCA(n_components=0.95, random_state=config.seed)),
                ("classifier", SVC(kernel="rbf", probability=True, random_state=config.seed)),
            ]
        )
    if config.model_type == "random_forest":
        return RandomForestClassifier(
            n_estimators=250,
            max_depth=None,
            min_samples_split=2,
            random_state=config.seed,
            n_jobs=-1,
        )
    if config.model_type == "logistic_regression":
        return Pipeline(
            [
                ("scaler", StandardScaler()),
                ("pca", PCA(n_components=0.95, random_state=config.seed)),
                ("classifier", LogisticRegression(max_iter=2000, random_state=config.seed)),
            ]
        )
    raise ValueError("Unsupported model type. Use: svm, random_forest, logistic_regression")
