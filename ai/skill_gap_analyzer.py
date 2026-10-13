import pandas as pd
from pathlib import Path


class SkillGapAnalyzer:
    """
    Identifies missing skills by comparing a student's current
    skills with the skills required for their target career.
    """

    def __init__(self, dataset_path=None):
        if dataset_path is None:
            project_root = Path(__file__).resolve().parent.parent
            dataset_path = project_root / "database" / "skills_dataset.csv"

        self.dataset_path = Path(dataset_path)
        self.skills_data = pd.read_csv(self.dataset_path)

    # careers_dataset.csv uses short names; skills_dataset.csv uses full names.
    SKILL_ALIASES = {
        "python": "Python Programming",
        "esp32": "ESP32 Development",
        "stm32": "STM32 Development",
        "oop": "Object-Oriented Programming",
    }

    @staticmethod
    def normalize_skill(skill):
        return str(skill).strip().casefold()

    @classmethod
    def canonical_skill(cls, skill):
        name = str(skill).strip()
        return cls.SKILL_ALIASES.get(name.casefold(), name)

    def analyze_skill_gaps(self, student_profile, career):
        """
        student_profile: Dictionary containing current_skills.
        career: Dictionary containing career_name and required_skills.
        """

        current_skills = student_profile.get("current_skills", [])
        required_skills = career.get("required_skills", [])

        if isinstance(required_skills, str):
            required_skills = [
                skill.strip()
                for skill in required_skills.split(";")
                if skill.strip()
            ]

        required_skills = [
            self.canonical_skill(skill) for skill in required_skills
        ]

        student_skill_levels = {}

        for item in current_skills:
            if isinstance(item, str):
                skill_name = item
                level = "Beginner"
            elif isinstance(item, dict):
                skill_name = item.get("skill", "")
                level = item.get("level", "Beginner")
            else:
                continue

            if skill_name:
                student_skill_levels[
                    self.normalize_skill(self.canonical_skill(skill_name))
                ] = {
                    "skill": str(skill_name).strip(),
                    "level": str(level).strip()
                }

        missing_skills = []
        matched_skills = []

        for required_skill in required_skills:
            normalized = self.normalize_skill(required_skill)

            if normalized in student_skill_levels:
                matched_skills.append({
                    "skill": required_skill,
                    "student_level": student_skill_levels[normalized]["level"]
                })
            else:
                missing_skills.append(required_skill)

        total_required = len(required_skills)
        total_matched = len(matched_skills)

        if total_required:
            coverage_percentage = round(
                (total_matched / total_required) * 100, 2
            )
        else:
            coverage_percentage = 0.0

        return {
            "success": True,
            "career": career.get("career_name", "Unknown Career"),
            "total_required_skills": total_required,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "total_matched_skills": total_matched,
            "total_missing_skills": len(missing_skills),
            "skill_coverage_percentage": coverage_percentage
        }

    def get_career_requirements(self, career_name):
        """
        Loads the career requirements from careers_dataset.csv.
        """

        project_root = Path(__file__).resolve().parent.parent
        careers_path = project_root / "database" / "careers_dataset.csv"

        careers_data = pd.read_csv(careers_path)

        matched = careers_data[
            careers_data["career_name"].str.casefold()
            == career_name.strip().casefold()
        ]

        if matched.empty:
            available = careers_data["career_name"].tolist()
            raise ValueError(
                f"Career '{career_name}' was not found. "
                f"Available careers: {', '.join(available)}"
            )

        row = matched.iloc[0]

        required_skills = [
            skill.strip()
            for skill in str(row["required_skills"]).split(";")
            if skill.strip()
        ]

        return {
            "career_id": row["career_id"],
            "career_name": row["career_name"],
            "department": row["department"],
            "required_skills": required_skills,
            "description": row["description"]
        }


if __name__ == "__main__":
    sample_profile = {
        "current_skills": [
            {"skill": "C Programming", "level": "Beginner"},
            {"skill": "Digital Electronics", "level": "Beginner"}
        ]
    }

    analyzer = SkillGapAnalyzer()

    target_career = analyzer.get_career_requirements(
        "Embedded Engineer"
    )

    result = analyzer.analyze_skill_gaps(
        sample_profile,
        target_career
    )

    print("SKILL GAP ANALYSIS SUCCESSFUL")
    print("-" * 40)
    print("Career:", result["career"])
    print("Required Skills:", result["total_required_skills"])
    print("Matched Skills:", result["total_matched_skills"])
    print("Missing Skills:", result["total_missing_skills"])
    print("Skill Coverage:", str(
        result["skill_coverage_percentage"]
    ) + "%")

    print("\nMatched Skills:")
    for item in result["matched_skills"]:
        print("-", item["skill"])

    print("\nMissing Skills:")
    for skill in result["missing_skills"]:
        print("-", skill)