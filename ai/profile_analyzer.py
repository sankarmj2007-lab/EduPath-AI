
class ProfileAnalyzer:
    """
    Analyzes a student's profile and validates the information
    needed to generate a personalized learning roadmap.
    """

    VALID_DEPARTMENTS = {
        "ECE",
        "CSE",
        "EEE",
        "MECH",
        "CIVIL",
        "IT",
        "OTHER",
        "ALL"
    }

    VALID_LEARNING_STYLES = {
        "Hands-on Projects",
        "Videos",
        "Reading",
        "Mixed"
    }

    def analyze_profile(self, student_profile):
        """
        Input: Student profile as a Python dictionary.
        Output: Validated profile with a summary and readiness score.
        """

        if not isinstance(student_profile, dict):
            raise ValueError("Student profile must be a dictionary.")

        required_fields = [
            "education_stage",
            "degree",
            "department",
            "study_year",
            "current_skills",
            "interests",
            "career_goal",
            "weekly_learning_hours",
            "learning_style"
        ]

        missing_fields = [
            field for field in required_fields
            if field not in student_profile
        ]

        if missing_fields:
            raise ValueError(
                "Missing required fields: " + ", ".join(missing_fields)
            )

        department = str(student_profile["department"]).strip().upper()

        if not department:
            raise ValueError("Department cannot be empty.")

        education_stage = str(
            student_profile["education_stage"]
        ).strip()

        degree = str(student_profile["degree"]).strip()
        career_goal = str(student_profile["career_goal"]).strip()
        learning_style = str(student_profile["learning_style"]).strip()

        if not education_stage:
            raise ValueError("Education stage cannot be empty.")

        if not degree:
            raise ValueError("Degree cannot be empty.")

        if not career_goal:
            raise ValueError("Career goal cannot be empty.")

        if not learning_style:
            raise ValueError("Learning style cannot be empty.")

        try:
            study_year = int(student_profile["study_year"])
            weekly_hours = float(
                student_profile["weekly_learning_hours"]
            )
        except (TypeError, ValueError):
            raise ValueError(
                "Study year must be an integer and weekly hours must be numeric."
            )

        if study_year < 1:
            raise ValueError("Study year must be at least 1.")

        if weekly_hours <= 0 or weekly_hours > 168:
            raise ValueError(
                "Weekly learning hours must be greater than 0 and at most 168."
            )

        current_skills = student_profile["current_skills"]
        interests = student_profile["interests"]

        if not isinstance(current_skills, list):
            raise ValueError("Current skills must be a list.")

        if not isinstance(interests, list):
            raise ValueError("Interests must be a list.")

        cleaned_skills = []

        for item in current_skills:
            if isinstance(item, str):
                skill_name = item.strip()
                skill_level = "Beginner"

            elif isinstance(item, dict):
                skill_name = str(item.get("skill", "")).strip()
                skill_level = str(
                    item.get("level", "Beginner")
                ).strip()

            else:
                raise ValueError(
                    "Each current skill must be a string or dictionary."
                )

            if not skill_name:
                raise ValueError("Skill names cannot be empty.")

            cleaned_skills.append({
                "skill": skill_name,
                "level": skill_level or "Beginner"
            })

        cleaned_interests = []

        for interest in interests:
            if not isinstance(interest, str) or not interest.strip():
                raise ValueError(
                    "Each interest must be a non-empty string."
                )

            cleaned_interests.append(interest.strip())

        analyzed_profile = {
            **student_profile,
            "education_stage": education_stage,
            "degree": degree,
            "department": department,
            "study_year": study_year,
            "current_skills": cleaned_skills,
            "interests": cleaned_interests,
            "career_goal": career_goal,
            "weekly_learning_hours": weekly_hours,
            "learning_style": learning_style
        }

        completed_fields = len(required_fields) - len(missing_fields)

        readiness_score = round(
            (completed_fields / len(required_fields)) * 100
        )

        return {
            "success": True,
            "profile": analyzed_profile,
            "summary": {
                "department": department,
                "career_goal": career_goal,
                "known_skills_count": len(cleaned_skills),
                "interests_count": len(cleaned_interests),
                "weekly_learning_hours": weekly_hours,
                "learning_style": learning_style
            },
            "readiness_score": readiness_score
        }


if __name__ == "__main__":
    sample_profile = {
        "student_id": "ST001",
        "name": "Sample Student",
        "education_stage": "College",
        "degree": "B.E.",
        "department": "ECE",
        "study_year": 2,
        "current_skills": [
            {"skill": "C Programming", "level": "Beginner"},
            {"skill": "Digital Electronics", "level": "Beginner"}
        ],
        "interests": [
            "Embedded Systems",
            "IoT",
            "Electronics"
        ],
        "career_goal": "Embedded Engineer",
        "weekly_learning_hours": 7,
        "learning_style": "Hands-on Projects"
    }

    analyzer = ProfileAnalyzer()
    result = analyzer.analyze_profile(sample_profile)

    print("PROFILE ANALYSIS SUCCESSFUL")
    print("-" * 35)
    print("Department:", result["summary"]["department"])
    print("Career Goal:", result["summary"]["career_goal"])
    print("Known Skills:", result["summary"]["known_skills_count"])
    print("Interests:", result["summary"]["interests_count"])
    print("Weekly Study Hours:",
          result["summary"]["weekly_learning_hours"])
    print("Learning Style:", result["summary"]["learning_style"])
    print("Readiness Score:", str(result["readiness_score"]) + "%")
