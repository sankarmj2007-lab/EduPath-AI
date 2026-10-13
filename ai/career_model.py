"""
EduPath AI - trained career prediction model.

Trains a Random Forest on database/student_profiles_dataset.csv and predicts
the top-N careers (with confidence) for a student profile.

Run from the project root:
    python ai/career_model.py train    # train, evaluate, save model + metrics
    python ai/career_model.py demo     # predict for a sample student

Use from other code (e.g. the Flask backend, later):
    from ai.career_model import predict_top_careers
    predict_top_careers({"department": "ECE", "study_year": 3, ...})

Outputs (folder `model/`):
    career_model.pkl         trained pipeline + metadata
    metrics.json             accuracy, top-3 accuracy, F1, feature importance
    confusion_matrix.csv     rows = real career, columns = predicted career
    confusion_matrix.png     (only if matplotlib is installed)

NOTE: the training data is synthetic. Quote these numbers as "on synthetic
data" and validate on real student responses before claiming real accuracy.
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    top_k_accuracy_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "database" / "student_profiles_dataset.csv"
MODEL_DIR = PROJECT_ROOT / "model"
MODEL_PATH = MODEL_DIR / "career_model.pkl"
METRICS_PATH = MODEL_DIR / "metrics.json"
CONFUSION_CSV_PATH = MODEL_DIR / "confusion_matrix.csv"
CONFUSION_PNG_PATH = MODEL_DIR / "confusion_matrix.png"

TARGET_COLUMN = "career"
ID_COLUMN = "student_id"
CATEGORICAL_COLUMNS = ["education_stage", "degree", "department", "learning_style"]
RANDOM_STATE = 42


# ----------------------------------------------------------------- training
def load_dataset():
    if not DATASET_PATH.exists():
        raise SystemExit(
            f"Dataset not found: {DATASET_PATH}\n"
            "Run database/generate_student_profiles.py first."
        )
    return pd.read_csv(DATASET_PATH)


def build_pipeline(feature_columns):
    categorical = [c for c in CATEGORICAL_COLUMNS if c in feature_columns]
    numeric = [c for c in feature_columns if c not in categorical]
    preprocessor = ColumnTransformer(
        [
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("numeric", "passthrough", numeric),
        ]
    )
    classifier = RandomForestClassifier(
        n_estimators=400,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    return Pipeline([("prep", preprocessor), ("model", classifier)])


def top_feature_importance(pipeline, limit=15):
    names = pipeline.named_steps["prep"].get_feature_names_out()
    names = [n.split("__", 1)[-1] for n in names]
    importances = pipeline.named_steps["model"].feature_importances_
    order = np.argsort(importances)[::-1][:limit]
    return [{"feature": names[i], "importance": round(float(importances[i]), 4)} for i in order]


def save_confusion_matrix(y_true, y_pred, classes):
    matrix = confusion_matrix(y_true, y_pred, labels=classes)
    pd.DataFrame(matrix, index=classes, columns=classes).to_csv(CONFUSION_CSV_PATH)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    fig, ax = plt.subplots(figsize=(14, 12))
    ax.imshow(matrix, cmap="Blues")
    ax.set_xticks(range(len(classes)), classes, rotation=90, fontsize=7)
    ax.set_yticks(range(len(classes)), classes, fontsize=7)
    ax.set_xlabel("Predicted career")
    ax.set_ylabel("Actual career")
    ax.set_title("Career model - confusion matrix (test set)")
    fig.tight_layout()
    fig.savefig(CONFUSION_PNG_PATH, dpi=150)
    plt.close(fig)
    return True


def train():
    data = load_dataset()
    features = data.drop(columns=[TARGET_COLUMN, ID_COLUMN])
    target = data[TARGET_COLUMN]

    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, stratify=target, random_state=RANDOM_STATE
    )

    pipeline = build_pipeline(list(features.columns))
    pipeline.fit(x_train, y_train)

    classes = list(pipeline.classes_)
    probabilities = pipeline.predict_proba(x_test)
    predictions = pipeline.predict(x_test)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(build_pipeline(list(features.columns)), features, target, cv=cv, n_jobs=1)

    metrics = {
        "rows": int(len(data)),
        "careers": len(classes),
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "top1_accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "top3_accuracy": round(float(top_k_accuracy_score(y_test, probabilities, k=3, labels=classes)), 4),
        "top5_accuracy": round(float(top_k_accuracy_score(y_test, probabilities, k=5, labels=classes)), 4),
        "macro_f1": round(float(f1_score(y_test, predictions, average="macro")), 4),
        "cv_5fold_top1_mean": round(float(cv_scores.mean()), 4),
        "cv_5fold_top1_std": round(float(cv_scores.std()), 4),
        "top_features": top_feature_importance(pipeline),
        "data_note": "Trained on synthetic data. Validate on real student responses.",
    }

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipeline,
            "feature_columns": list(features.columns),
            "numeric_defaults": features.select_dtypes("number").median().to_dict(),
            "categorical_defaults": {c: features[c].mode().iloc[0] for c in CATEGORICAL_COLUMNS},
            "classes": classes,
        },
        MODEL_PATH,
    )
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    png_saved = save_confusion_matrix(y_test, predictions, classes)

    print(f"Rows: {metrics['rows']}  |  Careers: {metrics['careers']}")
    print(f"Top-1 accuracy : {metrics['top1_accuracy']:.1%}")
    print(f"Top-3 accuracy : {metrics['top3_accuracy']:.1%}")
    print(f"Top-5 accuracy : {metrics['top5_accuracy']:.1%}")
    print(f"Macro F1       : {metrics['macro_f1']:.3f}")
    print(f"5-fold CV top-1: {metrics['cv_5fold_top1_mean']:.1%} (+/- {metrics['cv_5fold_top1_std']:.1%})")
    print("\nMost important features:")
    for item in metrics["top_features"][:10]:
        print(f"  {item['feature']:<40} {item['importance']:.4f}")
    print("\nPer-career report (test set):")
    print(classification_report(y_test, predictions, zero_division=0))
    print(f"Saved: {MODEL_PATH}")
    print(f"Saved: {METRICS_PATH}")
    print(f"Saved: {CONFUSION_CSV_PATH}")
    print(f"Saved: {CONFUSION_PNG_PATH}" if png_saved else "Confusion matrix PNG skipped (pip install matplotlib to enable).")


# --------------------------------------------------------------- prediction
_bundle_cache = None


def _load_bundle():
    global _bundle_cache
    if _bundle_cache is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained model not found: {MODEL_PATH}\nRun: python ai/career_model.py train"
            )
        _bundle_cache = joblib.load(MODEL_PATH)
    return _bundle_cache


def predict_top_careers(profile, top_n=3):
    """profile: dict using the dataset column names (see database/FEATURE_SCHEMA.md).
    Missing fields are filled with training-data defaults (median / most common).
    Returns [{"career": str, "confidence": float 0-100}, ...] best first."""
    bundle = _load_bundle()
    row = {}
    for column in bundle["feature_columns"]:
        if column in profile and profile[column] is not None:
            row[column] = profile[column]
        elif column in bundle["categorical_defaults"]:
            row[column] = bundle["categorical_defaults"][column]
        else:
            row[column] = bundle["numeric_defaults"].get(column, 0)
    frame = pd.DataFrame([row], columns=bundle["feature_columns"])

    probabilities = bundle["pipeline"].predict_proba(frame)[0]
    best = np.argsort(probabilities)[::-1][:top_n]
    return [
        {"career": bundle["classes"][i], "confidence": round(float(probabilities[i]) * 100, 1)}
        for i in best
    ]


def demo():
    sample = {
        "education_stage": "College",
        "degree": "B.E.",
        "department": "ECE",
        "study_year": 3,
        "cgpa": 8.1,
        "weekly_study_hours": 10,
        "learning_style": "Hands-on Projects",
        "skill_c_programming": 2,
        "skill_digital_electronics": 3,
        "skill_microcontrollers": 2,
        "skill_embedded_c": 2,
        "skill_sensors": 2,
        "skill_python": 1,
        "interest_embedded_systems": 1,
        "interest_iot": 1,
        "assessment_electronics": 82,
        "assessment_programming": 60,
        "pref_hardware_vs_software": 4,
        "projects_count": 3,
    }
    print("Sample student: ECE, year 3, embedded/IoT skills and interests\n")
    for rank, item in enumerate(predict_top_careers(sample), start=1):
        print(f"  {rank}. {item['career']:<30} {item['confidence']:>5.1f}%")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "train"
    if command == "train":
        train()
    elif command == "demo":
        demo()
    else:
        raise SystemExit("Usage: python ai/career_model.py [train|demo]")
