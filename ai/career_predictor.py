
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class CareerPredictor:
    """
    Recommends careers by comparing student profiles with
    career descriptions, required skills, and departments.
    Uses TF-IDF and cosine similarity.
    """

    def __init__(self, dataset_path=None):
        if dataset_path is None:
            project_root = Path(__file__).resolve().parent.parent
            dataset_path = project_root / "database" / "careers_dataset.csv"

        self.dataset_path = Path(dataset_path)
        self.careers = pd.read_csv(self.dataset_path).fillna("")

        self.career_documents = self.careers.apply(
            lambda row: " ".join([
                str(row["career_name"]),
                str(row["department"]),
                str(row["required_skills"]).replace(";", " "),
                str(row["description"])
            ]),
            axis=1
        )

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2)
        )

        self.career_vectors = self.vectorizer.fit_transform(
            self.career_documents
        )

    def predict_careers(self, student_profile, top_n=3):
        department = str(
            student_profile.get("department", "")
        ).strip()

        interests = student_profile.get("interests", [])
        current_skills = student_profile.get("current_skills", [])
        career_goal = str(
            student_profile.get("career_goal", "")
        ).strip()

        if isinstance(interests, str):
            interests = [interests]

        if isinstance(current_skills, str):
            current_skills = [current_skills]

        skill_names = []

        for item in current_skills:
            if isinstance(item, str):
                skill_names.append(item)
            elif isinstance(item, dict):
                skill = item.get("skill", "")
                if skill:
                    skill_names.append(str(skill))

        profile_text = " ".join(
            [department]
            + [str(item) for item in interests]
            + skill_names
            + [career_goal]
        )

        student_vector = self.vectorizer.transform([profile_text])

        similarity_scores = cosine_similarity(
            student_vector,
            self.career_vectors
        ).flatten()

        results = self.careers.copy()
        results["similarity_score"] = similarity_scores

        # Give a small relevance bonus to careers matching the department.
        results["department_bonus"] = results["department"].apply(
            lambda value: 0.10
            if str(value).strip().upper() in {
                department.upper(), "ALL"
            }
            else 0.0
        )

        results["prediction_score"] = (
            results["similarity_score"]
            + results["department_bonus"]
        )

        results = results.sort_values(
            by="prediction_score",
            ascending=False
        ).head(max(1, int(top_n)))

        recommendations = []

        for _, row in results.iterrows():
            recommendations.append({
                "career_id": str(row["career_id"]),
                "career_name": str(row["career_name"]),
                "department": str(row["department"]),
                "description": str(row["description"]),
                "similarity_score": round(
                    float(row["similarity_score"]), 4
                ),
                "prediction_score": round(
                    float(row["prediction_score"]), 4
                )
            })

        return {
            "success": True,
            "method": "TF-IDF and cosine similarity",
            "recommendations": recommendations
        }


if __name__ == "__main__":
    sample_profile = {
        "department": "ECE",
        "interests": [
            "Embedded Systems",
            "IoT",
            "Electronics"
        ],
        "current_skills": [
            {"skill": "C Programming", "level": "Beginner"},
            {"skill": "Digital Electronics", "level": "Beginner"}
        ],
        "career_goal": "Embedded Engineer"
    }

    predictor = CareerPredictor()
    result = predictor.predict_careers(sample_profile, top_n=3)

    print("CAREER PREDICTION SUCCESSFUL")
    print("-" * 40)
    print("Method:", result["method"])
    print("\nRecommended Careers:")

    for index, career in enumerate(
        result["recommendations"], start=1
    ):
        print(f"\n{index}. {career['career_name']}")
        print("   Department:", career["department"])
        print("   Prediction Score:", career["prediction_score"])
