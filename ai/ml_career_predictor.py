"""
EduPath AI - adapter that lets the Flask backend use the trained career model.

It converts the profile produced by ProfileAnalyzer into the feature columns the
model was trained on (see database/FEATURE_SCHEMA.md) and returns results in the
SAME format as CareerPredictor, so the frontend keeps working.

If the trained model is missing or broken, `available` is False and the backend
falls back to the old TF-IDF CareerPredictor. Train the model with:
    python ai/career_model.py train
"""

import difflib
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "model" / "career_model.pkl"
CAREERS_PATH = PROJECT_ROOT / "database" / "careers_dataset.csv"

SKILL_LEVELS = {"beginner": 1, "intermediate": 2, "advanced": 3}

# Skill names used in skills_dataset.csv / the form -> names used by the model.
SKILL_ALIASES = {
    "python programming": "python",
    "esp32 development": "esp32",
    "stm32 development": "stm32",
    "cmos design": "cmos",
    "oop": "object-oriented programming",
    "html5": "html",
    "css3": "css",
    "js": "javascript",
    "ml": "machine learning",
    "dl": "deep learning",
    "sklearn": "scikit-learn",
    "rest api": "rest apis",
}

# Words found in the interests text -> interest_* column of the model.
INTEREST_KEYWORDS = {
    "interest_embedded_systems": ["embedded", "firmware", "microcontroller"],
    "interest_iot": ["iot", "internet of things", "sensor", "smart device"],
    "interest_artificial_intelligence": ["ai", "artificial", "machine learning",
                                         "deep learning", "ml", "neural", "vision"],
    "interest_data_analytics": ["data", "analytics", "analysis", "statistics", "visualization"],
    "interest_web_development": ["web", "frontend", "front end", "backend", "html", "website"],
    "interest_mobile_apps": ["mobile", "android", "ios", "app development"],
    "interest_software_engineering": ["software", "programming", "coding", "algorithm", "development"],
    "interest_game_development": ["game", "gaming", "unity"],
    "interest_cybersecurity": ["security", "cyber", "hacking", "ethical"],
    "interest_cloud_devops": ["cloud", "devops", "aws", "azure", "docker", "kubernetes"],
    "interest_databases": ["database", "sql", "dba"],
    "interest_networking": ["network", "routing", "protocol"],
    "interest_vlsi_digital_design": ["vlsi", "digital design", "verilog", "fpga", "asic", "chip"],
    "interest_analog_pcb_design": ["analog", "pcb", "circuit"],
    "interest_signal_processing": ["signal", "dsp", "image processing"],
    "interest_communication_systems": ["communication", "wireless", "5g", "antenna"],
    "interest_robotics": ["robot", "automation", "drone", "control system"],
}


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")


def _word_match(keyword, text):
    """Whole-word match so 'ai' does not match 'detail'."""
    return re.search(r"(?<![a-z0-9])" + re.escape(keyword) + r"(?![a-z0-9])", text) is not None


class MLCareerPredictor:
    """Random Forest career predictor with a safe 'available' flag."""

    def __init__(self, model_path=None):
        self.available = False
        self.load_error = None
        self.model_path = Path(model_path) if model_path else MODEL_PATH
        try:
            self._bundle = joblib.load(self.model_path)
            self._careers = pd.read_csv(CAREERS_PATH).fillna("").set_index("career_name")
            self._feature_columns = self._bundle["feature_columns"]
            self._skill_columns = {
                column[len("skill_"):]: column
                for column in self._feature_columns if column.startswith("skill_")
            }
            self.available = True
        except Exception as error:  # model missing, corrupt, wrong sklearn version
            self.load_error = str(error)

    # ---------------------------------------------------------- feature build
    def _skill_column(self, skill_name):
        name = str(skill_name).strip().lower()
        name = SKILL_ALIASES.get(name, name)
        slug = slugify(name)
        if slug in self._skill_columns:
            return self._skill_columns[slug]
        close = difflib.get_close_matches(slug, list(self._skill_columns), n=1, cutoff=0.88)
        return self._skill_columns[close[0]] if close else None

    def build_features(self, profile):
        """Returns (feature_row, defaulted_feature_count)."""
        bundle = self._bundle
        row = {}

        direct = {
            "education_stage": profile.get("education_stage"),
            "degree": profile.get("degree"),
            "department": profile.get("department"),
            "study_year": profile.get("study_year"),
            "weekly_study_hours": profile.get("weekly_learning_hours"),
            "learning_style": profile.get("learning_style"),
        }
        for column, value in direct.items():
            if value not in (None, ""):
                row[column] = value

        for column in self._skill_columns.values():
            row[column] = 0
        for item in profile.get("current_skills", []):
            skill = item.get("skill") if isinstance(item, dict) else item
            level_text = item.get("level", "Beginner") if isinstance(item, dict) else "Beginner"
            column = self._skill_column(skill)
            if column:
                level = SKILL_LEVELS.get(str(level_text).strip().lower(), 1)
                row[column] = max(row[column], level)

        interests_text = " ".join(str(i).lower() for i in profile.get("interests", []))
        for column, keywords in INTEREST_KEYWORDS.items():
            if column in self._feature_columns:
                row[column] = int(any(_word_match(k, interests_text) for k in keywords))

        defaulted = 0
        for column in self._feature_columns:
            if column in row:
                continue
            defaulted += 1
            if column in bundle["categorical_defaults"]:
                row[column] = bundle["categorical_defaults"][column]
            else:
                row[column] = bundle["numeric_defaults"].get(column, 0)
        return row, defaulted

    # --------------------------------------------------------------- predict
    def predict_careers(self, student_profile, top_n=3):
        if not self.available:
            raise RuntimeError(f"ML model not available: {self.load_error}")

        row, defaulted = self.build_features(student_profile)
        frame = pd.DataFrame([row], columns=self._feature_columns)
        probabilities = self._bundle["pipeline"].predict_proba(frame)[0]
        classes = self._bundle["classes"]

        recommendations = []
        for index in np.argsort(probabilities)[::-1][:max(1, int(top_n))]:
            career_name = classes[index]
            info = self._careers.loc[career_name] if career_name in self._careers.index else None
            score = round(float(probabilities[index]), 4)
            recommendations.append({
                "career_id": str(info["career_id"]) if info is not None else "",
                "career_name": career_name,
                "department": str(info["department"]) if info is not None else "",
                "description": str(info["description"]) if info is not None else "",
                "confidence": round(score * 100, 1),
                # kept so the existing frontend keeps working
                "similarity_score": score,
                "prediction_score": score,
            })

        return {
            "success": True,
            "method": "Random Forest (trained ML model)",
            "inputs_defaulted": defaulted,
            "inputs_total": len(self._feature_columns),
            "recommendations": recommendations,
        }


if __name__ == "__main__":
    predictor = MLCareerPredictor()
    if not predictor.available:
        raise SystemExit(f"Model not available: {predictor.load_error}")
    sample = {
        "education_stage": "College", "degree": "B.E.", "department": "ECE",
        "study_year": 2,
        "current_skills": [
            {"skill": "C Programming", "level": "Beginner"},
            {"skill": "Digital Electronics", "level": "Beginner"},
        ],
        "interests": ["Embedded Systems", "IoT", "Electronics"],
        "career_goal": "Embedded Engineer",
        "weekly_learning_hours": 7, "learning_style": "Hands-on Projects",
    }
    result = predictor.predict_careers(sample)
    print(result["method"], f"({result['inputs_defaulted']}/{result['inputs_total']} inputs defaulted)")
    for item in result["recommendations"]:
        print(f"  {item['career_name']:<28} {item['confidence']:>5.1f}%")
