
from pathlib import Path
import pandas as pd


class RoadmapGenerator:
    """
    Generates a personalized learning roadmap using:
    1. Missing skills from the skill-gap analyzer.
    2. Skill prerequisites from the skills dataset.
    3. Estimated learning hours.
    4. The student's weekly learning availability.
    5. Skills the student already knows.
    """

    def __init__(self, dataset_path=None):
        if dataset_path is None:
            project_root = Path(__file__).resolve().parent.parent
            dataset_path = project_root / "database" / "skills_dataset.csv"

        self.dataset_path = Path(dataset_path)
        self.skills_data = pd.read_csv(self.dataset_path).fillna("")

        self.skill_lookup = {}

        for _, row in self.skills_data.iterrows():
            key = self.normalize(row["skill_name"])
            self.skill_lookup[key] = row.to_dict()

    @staticmethod
    def normalize(value):
        return str(value).strip().casefold()

    @staticmethod
    def parse_list(value):
        if not value or str(value).strip().casefold() == "none":
            return []

        return [
            item.strip()
            for item in str(value).split(";")
            if item.strip()
        ]

    def get_skill_details(self, skill_name):
        return self.skill_lookup.get(self.normalize(skill_name))

    def generate_roadmap(
        self,
        missing_skills,
        weekly_learning_hours=7,
        current_skills=None,
    ):
        if weekly_learning_hours <= 0:
            raise ValueError(
                "Weekly learning hours must be greater than 0."
            )

        if isinstance(missing_skills, dict):
            missing_skills = missing_skills.get("missing_skills", [])

        if not isinstance(missing_skills, list):
            raise ValueError("Missing skills must be provided as a list.")

        if current_skills is None:
            current_skills = []

        if not isinstance(current_skills, list):
            raise ValueError("Current skills must be provided as a list.")

        # Collect the skills the student already knows.
        known_skill_names = set()

        for item in current_skills:
            if isinstance(item, dict):
                skill_name = item.get(
                    "skill",
                    item.get("skill_name", "")
                )
            else:
                skill_name = item

            skill_name = str(skill_name).strip()

            if skill_name:
                known_skill_names.add(self.normalize(skill_name))

        # Remove empty, duplicate, and already-known skills.
        requested_skills = []
        requested_keys = set()

        for item in missing_skills:
            if isinstance(item, dict):
                skill_name = item.get(
                    "skill",
                    item.get("skill_name", "")
                )
            else:
                skill_name = item

            skill_name = str(skill_name).strip()
            key = self.normalize(skill_name)

            if (
                skill_name
                and key not in requested_keys
                and key not in known_skill_names
            ):
                requested_skills.append(skill_name)
                requested_keys.add(key)

        selected = {}
        processing = set()

        def add_skill(skill_name):
            key = self.normalize(skill_name)

            # Do not add skills the student already knows.
            if key in known_skill_names:
                return

            if key in selected or key in processing:
                return

            details = self.get_skill_details(skill_name)

            if details is None:
                selected[key] = {
                    "skill_name": skill_name,
                    "category": "General",
                    "level": "Not specified",
                    "estimated_hours": 10,
                    "prerequisites": [],
                    "known_in_dataset": False,
                }
                return

            processing.add(key)

            prerequisites = self.parse_list(
                details.get("prerequisites", "")
            )

            # Add prerequisites first, except skills already known.
            for prerequisite in prerequisites:
                if self.get_skill_details(prerequisite) is not None:
                    add_skill(prerequisite)

            selected[key] = {
                "skill_name": str(details["skill_name"]),
                "category": str(details["category"]),
                "level": str(details["level"]),
                "estimated_hours": max(
                    1,
                    int(float(details["estimated_hours"]))
                ),
                "prerequisites": prerequisites,
                "known_in_dataset": True,
            }

            processing.remove(key)

        for skill in requested_skills:
            add_skill(skill)

        # Arrange skills so prerequisites appear before dependent skills.
        ordered = []
        visited = set()
        visiting = set()

        def visit(key):
            if key in visited or key in visiting:
                return

            if key not in selected:
                return

            visiting.add(key)
            details = selected[key]

            for prerequisite in details["prerequisites"]:
                prerequisite_key = self.normalize(prerequisite)

                if prerequisite_key in selected:
                    visit(prerequisite_key)

            visiting.remove(key)
            visited.add(key)
            ordered.append(details)

        for key in selected:
            visit(key)

        weekly_hours = float(weekly_learning_hours)

        total_hours = sum(
            item["estimated_hours"] for item in ordered
        )

        roadmap = []
        accumulated_hours = 0

        for index, item in enumerate(ordered, start=1):
            hours = item["estimated_hours"]
            start_hours = accumulated_hours
            accumulated_hours += hours

            start_week = int(start_hours // weekly_hours) + 1

            end_week = max(
                start_week,
                int((accumulated_hours - 1) // weekly_hours) + 1
            )

            roadmap.append({
                "step": index,
                "skill": item["skill_name"],
                "category": item["category"],
                "level": item["level"],
                "estimated_hours": hours,
                "prerequisites": item["prerequisites"],
                "week": (
                    start_week
                    if start_week == end_week
                    else f"{start_week}-{end_week}"
                ),
                "known_in_dataset": item["known_in_dataset"],
            })

        estimated_weeks = (
            int(total_hours // weekly_hours)
            + (1 if total_hours % weekly_hours else 0)
        )

        return {
            "success": True,
            "total_skills": len(roadmap),
            "total_learning_hours": total_hours,
            "weekly_learning_hours": weekly_hours,
            "estimated_duration_weeks": estimated_weeks,
            "roadmap": roadmap,
        }


if __name__ == "__main__":
    sample_missing_skills = [
        "Embedded C",
        "Microcontrollers",
        "ESP32",
        "STM32",
        "RTOS",
        "Embedded Linux",
    ]

    generator = RoadmapGenerator()

    result = generator.generate_roadmap(
        missing_skills=sample_missing_skills,
        weekly_learning_hours=7,
        current_skills=["C Programming"],
    )

    print("ROADMAP GENERATION SUCCESSFUL")
    print("-" * 40)
    print("Total Skills:", result["total_skills"])
    print("Total Learning Hours:", result["total_learning_hours"])
    print("Weekly Learning Hours:", result["weekly_learning_hours"])
    print(
        "Estimated Duration:",
        result["estimated_duration_weeks"],
        "weeks",
    )

    print("\nPersonalized Learning Roadmap:")

    for item in result["roadmap"]:
        print(
            f"\nStep {item['step']}: {item['skill']}"
            f"\n  Level: {item['level']}"
            f"\n  Estimated Hours: {item['estimated_hours']}"
            f"\n  Suggested Week: {item['week']}"
            f"\n  Prerequisites: "
            f"{', '.join(item['prerequisites']) or 'None'}"
        )
