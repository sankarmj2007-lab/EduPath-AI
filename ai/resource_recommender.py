
import json
from pathlib import Path


class ResourceRecommender:
    """
    Recommends learning resources for roadmap skills.
    Supports equivalent skill names without duplicating resources.
    """

    SKILL_ALIASES = {
        "python": "python programming",
        "esp32": "esp32 development",
        "stm32": "stm32 development",
        "oop": "object-oriented programming",
    }

    def __init__(self, resources_path=None):
        if resources_path is None:
            project_root = Path(__file__).resolve().parent.parent
            resources_path = project_root / "database" / "resources.json"

        self.resources_path = Path(resources_path)

        with open(self.resources_path, "r", encoding="utf-8") as file:
            self.resources = json.load(file)

        if not isinstance(self.resources, list):
            raise ValueError("resources.json must contain a JSON array.")

    @staticmethod
    def normalize(value):
        return str(value).strip().casefold()

    def canonical_skill(self, skill_name):
        normalized = self.normalize(skill_name)
        return self.SKILL_ALIASES.get(normalized, normalized)

    def recommend_resources(self, skills, max_per_skill=3):
        """
        skills can be skill names or roadmap step dictionaries.
        Returns matching resources grouped by skill.
        """

        if isinstance(skills, dict):
            skills = skills.get("roadmap", [])

        if not isinstance(skills, list):
            raise ValueError("Skills must be provided as a list.")

        if max_per_skill < 1:
            raise ValueError("max_per_skill must be at least 1.")

        recommendations = []

        for item in skills:
            if isinstance(item, dict):
                skill_name = item.get(
                    "skill",
                    item.get("skill_name", "")
                )
            else:
                skill_name = str(item)

            skill_name = str(skill_name).strip()

            if not skill_name:
                continue

            matched_resources = []
            target_skill = self.canonical_skill(skill_name)

            for resource in self.resources:
                resource_skill = resource.get(
                    "skill",
                    resource.get("related_skill", "")
                )

                if self.canonical_skill(resource_skill) == target_skill:
                    matched_resources.append({
                        "title": resource.get("title", "Untitled Resource"),
                        "type": resource.get("type", "Other"),
                        "url": resource.get("url", ""),
                        "platform": resource.get("platform", "Not specified"),
                        "level": resource.get("level", "All levels")
                    })

                if len(matched_resources) >= max_per_skill:
                    break

            recommendations.append({
                "skill": skill_name,
                "resource_count": len(matched_resources),
                "resources": matched_resources
            })

        total_resources = sum(
            item["resource_count"] for item in recommendations
        )

        return {
            "success": True,
            "skills_processed": len(recommendations),
            "total_resources": total_resources,
            "recommendations": recommendations
        }


if __name__ == "__main__":
    sample_skills = [
        "C Programming",
        "Python",
        "HTML",
        "ESP32",
        "STM32",
        "OOP"
    ]

    recommender = ResourceRecommender()
    result = recommender.recommend_resources(sample_skills)

    print("RESOURCE RECOMMENDATION TEST")
    print("-" * 40)
    print("Skills Processed:", result["skills_processed"])
    print("Total Resources Found:", result["total_resources"])

    for item in result["recommendations"]:
        print(f"\nSkill: {item['skill']}")
        print("Resources Found:", item["resource_count"])

        if not item["resources"]:
            print("  No matching resource found in the dataset.")

        for resource in item["resources"]:
            print("  Title:", resource["title"])
