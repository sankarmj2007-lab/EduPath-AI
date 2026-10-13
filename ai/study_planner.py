
from datetime import date, timedelta


class StudyPlanner:
    """
    Creates a weekly study plan from a personalized learning roadmap
    and the student's available study hours.
    """

    def generate_study_plan(
        self,
        roadmap,
        weekly_learning_hours=7,
        start_date=None
    ):
        if isinstance(roadmap, dict):
            roadmap = roadmap.get("roadmap", [])

        if not isinstance(roadmap, list):
            raise ValueError("Roadmap must be provided as a list.")

        weekly_hours = float(weekly_learning_hours)

        if weekly_hours <= 0 or weekly_hours > 168:
            raise ValueError(
                "Weekly learning hours must be greater than 0 and at most 168."
            )

        if start_date is None:
            start_date = date.today()
        elif isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)

        if not isinstance(start_date, date):
            raise ValueError(
                "start_date must be a date or an ISO date string."
            )

        # Divide weekly hours across seven days.
        daily_hours = weekly_hours / 7

        # Use a practical maximum of 3 study hours per day.
        daily_hours = min(daily_hours, 3.0)

        plan = []
        current_day = start_date
        remaining_daily_hours = daily_hours
        week_number = 1
        total_planned_hours = 0.0

        for step in roadmap:
            skill_name = step.get("skill", step.get("skill_name", "Unknown Skill"))
            estimated_hours = float(step.get("estimated_hours", 1))

            if estimated_hours <= 0:
                continue

            remaining_skill_hours = estimated_hours

            while remaining_skill_hours > 0:
                if remaining_daily_hours <= 0.0001:
                    current_day += timedelta(days=1)
                    remaining_daily_hours = daily_hours

                    days_elapsed = (current_day - start_date).days
                    week_number = days_elapsed // 7 + 1

                session_hours = min(
                    remaining_skill_hours,
                    remaining_daily_hours
                )

                plan.append({
                    "date": current_day.isoformat(),
                    "week": week_number,
                    "skill": skill_name,
                    "study_hours": round(session_hours, 2),
                    "activity": f"Learn and practice {skill_name}"
                })

                total_planned_hours += session_hours
                remaining_skill_hours -= session_hours
                remaining_daily_hours -= session_hours

        weekly_summary = {}

        for session in plan:
            week = session["week"]
            weekly_summary[week] = round(
                weekly_summary.get(week, 0) + session["study_hours"],
                2
            )

        return {
            "success": True,
            "start_date": start_date.isoformat(),
            "weekly_learning_hours": weekly_hours,
            "planned_sessions": len(plan),
            "total_planned_hours": round(total_planned_hours, 2),
            "estimated_duration_days": (
                (date.fromisoformat(plan[-1]["date"]) - start_date).days + 1
                if plan else 0
            ),
            "weekly_summary": [
                {
                    "week": week,
                    "planned_hours": hours
                }
                for week, hours in sorted(weekly_summary.items())
            ],
            "study_plan": plan
        }


if __name__ == "__main__":
    sample_roadmap = [
        {"skill": "C Programming", "estimated_hours": 10},
        {"skill": "Embedded C", "estimated_hours": 15},
        {"skill": "ESP32 Development", "estimated_hours": 12}
    ]

    planner = StudyPlanner()

    result = planner.generate_study_plan(
        roadmap=sample_roadmap,
        weekly_learning_hours=7,
        start_date="2026-10-12"
    )

    print("STUDY PLANNER SUCCESSFUL")
    print("-" * 40)
    print("Start Date:", result["start_date"])
    print("Weekly Learning Hours:", result["weekly_learning_hours"])
    print("Total Planned Hours:", result["total_planned_hours"])
    print("Planned Sessions:", result["planned_sessions"])
    print("Estimated Duration:", result["estimated_duration_days"], "days")

    print("\nWeekly Summary:")
    for item in result["weekly_summary"]:
        print(
            f"Week {item['week']}: "
            f"{item['planned_hours']} hours"
        )

    print("\nFirst 10 Study Sessions:")
    for session in result["study_plan"][:10]:
        print(
            f"{session['date']} | "
            f"{session['skill']} | "
            f"{session['study_hours']} hours"
        )
