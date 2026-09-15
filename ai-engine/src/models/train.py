"""
Model training, evaluation, and model selection pipeline.
Compares Logistic Regression and Random Forest on Recall, F1, and ROC-AUC.
"""

from typing import Any, Dict, Tuple
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.models.model_utils import save_metadata, save_model
from src.preprocessing.preprocess import FEATURE_COLUMNS, preprocess_dataframe


def evaluate_model(model: Any, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
    """Compute standard classification evaluation metrics."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

    return {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
    }


def train_and_compare_models(df: pd.DataFrame) -> Tuple[Any, Dict[str, Any]]:
    """
    Train Logistic Regression and Random Forest, compare metrics, and return the best model.
    """
    X, y = preprocess_dataframe(df, is_training=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # 1. Logistic Regression Pipeline (StandardScaler + LogisticRegression)
    lr_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(random_state=42, class_weight="balanced", max_iter=500)),
    ])
    lr_pipeline.fit(X_train, y_train)
    lr_metrics = evaluate_model(lr_pipeline, X_test, y_test)

    # 2. Random Forest Classifier
    rf_classifier = RandomForestClassifier(
        n_estimators=120,
        max_depth=7,
        min_samples_split=4,
        random_state=42,
        class_weight="balanced",
    )
    rf_classifier.fit(X_train, y_train)
    rf_metrics = evaluate_model(rf_classifier, X_test, y_test)

    # Selection logic: prioritize ROC-AUC and F1 for predictive maintenance anomaly detection
    rf_score = (rf_metrics["roc_auc"] * 0.5) + (rf_metrics["f1"] * 0.3) + (rf_metrics["recall"] * 0.2)
    lr_score = (lr_metrics["roc_auc"] * 0.5) + (lr_metrics["f1"] * 0.3) + (lr_metrics["recall"] * 0.2)

    if rf_score >= lr_score:
        best_model_name = "RandomForest"
        best_model = rf_classifier
        best_metrics = rf_metrics
    else:
        best_model_name = "LogisticRegression"
        best_model = lr_pipeline
        best_metrics = lr_metrics

    # Feature importances extraction
    feature_importances = {}
    if hasattr(best_model, "feature_importances_"):
        feature_importances = dict(zip(FEATURE_COLUMNS, [round(float(v), 4) for v in best_model.feature_importances_]))
    elif hasattr(best_model, "named_steps") and hasattr(best_model.named_steps["classifier"], "coef_"):
        coefs = best_model.named_steps["classifier"].coef_[0]
        feature_importances = dict(zip(FEATURE_COLUMNS, [round(float(abs(v)), 4) for v in coefs]))

    metadata = {
        "selected_model": best_model_name,
        "selected_metrics": best_metrics,
        "comparison": {
            "LogisticRegression": lr_metrics,
            "RandomForest": rf_metrics,
        },
        "feature_importances": feature_importances,
        "feature_columns": FEATURE_COLUMNS,
        "training_samples": len(df),
    }


    # Save artifacts
    save_model(best_model)
    save_metadata(metadata)

    return best_model, metadata
