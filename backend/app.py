from pathlib import Path
import json
import math
import re
import sys

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.profile_analyzer import ProfileAnalyzer
from ai.skill_gap_analyzer import SkillGapAnalyzer
from ai.career_predictor import CareerPredictor
from ai.ml_career_predictor import MLCareerPredictor
from ai.roadmap_generator import RoadmapGenerator
from ai.resource_recommender import ResourceRecommender
from ai.study_planner import StudyPlanner

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

# Existing college AI modules
profile_analyzer = ProfileAnalyzer()
skill_gap_analyzer = SkillGapAnalyzer()
career_predictor = CareerPredictor()
ml_career_predictor = MLCareerPredictor()
roadmap_generator = RoadmapGenerator()
resource_recommender = ResourceRecommender()
study_planner = StudyPlanner()

DATABASE_DIR = PROJECT_ROOT / "database"


def normalize(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip().lower())


def canonical_subject(value):
    """Make common subject names equivalent."""
    subject = normalize(value)
    aliases = {
        "maths": "mathematics",
        "math": "mathematics",
        "bio": "biology",
        "cs": "computer science",
        "computer applications": "computer science",
    }
    return aliases.get(subject, subject)


def get_value(data, *keys, default=""):
    for key in keys:
        value = data.get(key)
        if value is not None and str(value).strip():
            return value
    return default


def as_list(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def load_csv(filename):
    path = DATABASE_DIR / filename
    if not path.exists():
        app.logger.warning("Dataset not found: %s", path)
        return pd.DataFrame()

    try:
        return pd.read_csv(path).fillna("")
    except (OSError, pd.errors.ParserError, UnicodeDecodeError):
        app.logger.exception("Could not load CSV: %s", filename)
        return pd.DataFrame()


def load_json(filename):
    path = DATABASE_DIR / filename
    if not path.exists():
        app.logger.warning("JSON file not found: %s", path)
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            for key in ("resources", "items", "data"):
                if isinstance(data.get(key), list):
                    return data[key]
            return [data]

    except (OSError, json.JSONDecodeError):
        app.logger.exception("Could not load JSON: %s", filename)

    return []


def find_column(row, *names):
    normalized_row = {
        normalize(key).replace(" ", "_"): value
        for key, value in row.items()
    }

    for name in names:
        key = normalize(name).replace(" ", "_")
        if key in normalized_row:
            value = normalized_row[key]
            if value is not None and str(value).strip():
                return value

    return ""


def board_matches(row_board, requested_board):
    row_value = normalize(row_board)
    requested = normalize(requested_board)

    if not row_value or not requested:
        return True

    tn_terms = ("tamil nadu", "samacheer", "state board", "tn state")
    cbse_terms = ("cbse", "ncert", "central board")

    if any(term in requested for term in tn_terms):
        return any(term in row_value for term in tn_terms)

    if any(term in requested for term in cbse_terms):
        return any(term in row_value for term in cbse_terms)

    return requested in row_value or row_value in requested


def class_matches(row_class, requested_class):
    row_digits = re.search(r"\d+", str(row_class))
    requested_digits = re.search(r"\d+", str(requested_class))

    if not row_digits or not requested_digits:
        return True

    return row_digits.group() == requested_digits.group()


# ==================================================
# SCHOOL STUDY PLANNING
# ==================================================

# Hours a student realistically needs for ONE topic (learn + practise).
SCHOOL_TOPIC_HOURS = {
    "mathematics": 5,
    "physics": 4,
    "chemistry": 4,
    "biology": 4,
    "computer science": 4,
    "science": 4,
    "english": 3,
    "social science": 3,
}
DEFAULT_TOPIC_HOURS = 3

# Goals change how deep the preparation needs to be.
SCHOOL_GOAL_FACTOR = {
    "school exams": 1.0,
    "board exams": 1.25,
    "entrance exams": 1.5,
    "career exploration": 0.75,
}

# Share of every week used for new topics. The rest is revision.
STUDY_SHARE_OF_WEEK = 0.8


def round_half(value):
    """Round to the nearest 0.5 hour."""
    return round(value * 2) / 2


def format_hours(value):
    number = float(value)
    text = str(int(number)) if number == int(number) else str(number)
    return f"{text} hour" if number == 1 else f"{text} hours"


def school_topic_hours(subject, goal):
    base = SCHOOL_TOPIC_HOURS.get(
        canonical_subject(subject), DEFAULT_TOPIC_HOURS
    )
    factor = SCHOOL_GOAL_FACTOR.get(normalize(goal), 1.0)
    return max(1.0, round_half(base * factor))


def interleave_by_subject(roadmap):
    """Mix subjects (Maths, Physics, Chemistry, ...) so every week has
    variety, while keeping each subject's syllabus order."""
    groups = {}
    for item in roadmap:
        groups.setdefault(item["subject"], []).append(dict(item))

    mixed = []
    queues = list(groups.values())
    while any(queues):
        for queue in queues:
            if queue:
                mixed.append(queue.pop(0))
    return mixed


def build_school_study_plan(roadmap, weekly_hours, goal):
    """Turn the topic roadmap into a week-by-week plan.

    Every week: new topics (about 80 percent of the hours) plus a
    revision and self-test session. Board and entrance goals end with
    a final revision week and a mock test week.
    """
    plan = []
    topics = interleave_by_subject(roadmap)
    subjects = []
    for item in topics:
        if item["subject"] not in subjects:
            subjects.append(item["subject"])

    study_capacity = max(1.0, math.floor(weekly_hours * STUDY_SHARE_OF_WEEK * 2) / 2)
    revision_hours = round_half(max(0.0, weekly_hours - study_capacity))

    state = {"week": 1, "left": study_capacity, "covered": []}

    def add_session(week, topic, subject, activity, hours, notes=""):
        plan.append({
            "day": len(plan) + 1,
            "week": week,
            "topic": topic,
            "subject": subject,
            "activity": activity,
            "hours": round(hours, 2),
            "estimated_hours": round(hours, 2),
            "notes": notes,
        })

    def close_week():
        if revision_hours >= 0.5 and state["covered"]:
            shown = state["covered"][:4]
            extra = len(state["covered"]) - len(shown)
            notes = "Revise: " + ", ".join(shown)
            if extra > 0:
                notes += f" and {extra} more"
            add_session(
                state["week"], "Revision and self-test", "Weekly Revision",
                "Revision", revision_hours, notes,
            )
        state["week"] += 1
        state["left"] = study_capacity
        state["covered"] = []

    for item in topics:
        remaining = float(item["estimated_hours"])
        started = False

        while remaining > 0.01:
            # If only a small slot is left this week, do not start a new
            # topic. Use the slot for extra practice on topics already
            # studied, then begin the new topic next week.
            if (
                not started
                and state["covered"]
                and state["left"] < min(remaining, 2.0)
            ):
                if state["left"] >= 0.5:
                    shown = state["covered"][:3]
                    add_session(
                        state["week"], "Extra practice", "Practice",
                        "Practice", state["left"],
                        "Practise questions on: " + ", ".join(shown),
                    )
                state["left"] = 0

            if state["left"] <= 0.01:
                close_week()
                continue

            take = min(remaining, state["left"])
            add_session(
                state["week"], item["title"], item["subject"],
                "Continue practice" if started else "Learn and practise",
                take,
            )
            if item["title"] not in state["covered"]:
                state["covered"].append(item["title"])
            started = True
            remaining -= take
            state["left"] -= take

            if state["left"] <= 0.01:
                close_week()

    if state["covered"]:
        close_week()

    last_week = state["week"] - 1
    per_subject = max(0.5, math.floor(weekly_hours / max(1, len(subjects)) * 2) / 2)
    goal_key = normalize(goal)

    if goal_key != "career exploration" and subjects:
        last_week += 1
        for subject in subjects:
            add_session(
                last_week, f"Revise all {subject} chapters", subject,
                "Final revision", per_subject,
                "Go through short notes and solved examples.",
            )

    if goal_key in ("board exams", "entrance exams") and subjects:
        last_week += 1
        for subject in subjects:
            add_session(
                last_week, f"Timed mock paper: {subject}", subject,
                "Mock test", per_subject,
                "Solve under exam conditions, then check mistakes.",
            )

    return plan


def build_school_roadmap(profile):
    board = profile["school_board"]
    class_level = profile["school_class"]
    stream = normalize(profile["school_stream"])
    subjects = profile["school_subjects"]
    goal = profile["school_goal"]

    curriculum = load_csv("school_curriculum_dataset.csv")
    roadmap = []

    requested_subjects = {
        canonical_subject(subject) for subject in subjects
    }

    for _, series in curriculum.iterrows():
        row = series.to_dict()

        row_board = find_column(
            row, "board", "education_board", "curriculum"
        )
        row_class = find_column(
            row, "class", "class_level", "grade", "standard"
        )
        row_stream = find_column(row, "stream", "group")
        row_subject = find_column(
            row, "subject", "subject_name", "course"
        )

        if row_board and not board_matches(row_board, board):
            continue

        if row_class and not class_matches(row_class, class_level):
            continue

        if row_subject and requested_subjects:
            curriculum_subject = canonical_subject(row_subject)
            if curriculum_subject not in requested_subjects:
                continue

        # Stream matching is deliberately flexible. The subject selection
        # takes priority, so a selected subject is not silently excluded
        # just because the profile's group label differs.
        if row_stream and not subjects:
            normalized_row_stream = normalize(row_stream)
            if (
                normalized_row_stream not in ("general", "all")
                and stream not in ("", "general", "all")
                and normalized_row_stream not in stream
                and stream not in normalized_row_stream
            ):
                continue

        topic = find_column(
            row,
            "topic",
            "topics",
            "chapter",
            "chapter_name",
            "unit",
            "unit_name",
            "learning_topic",
        )

        description = find_column(
            row, "description", "learning_outcome", "details"
        )

        if not topic:
            topic = row_subject or "Review your selected subjects"

        # Curriculum CSV stores multiple topics separated by semicolons.
        topic_list = [
            item.strip()
            for item in str(topic).split(";")
            if item.strip()
        ] or [str(topic)]

        # Use hours from the dataset when it provides them. The current
        # dataset has no hours column, so hours come from the subject
        # and the student's goal.
        dataset_hours = find_column(
            row, "estimated_hours", "study_hours", "hours"
        )

        try:
            topic_hours = max(1, float(dataset_hours) / len(topic_list))
        except (ValueError, TypeError):
            topic_hours = school_topic_hours(row_subject, goal)

        for topic_name in topic_list:
            roadmap.append({
                "title": topic_name,
                "topic": topic_name,
                "subject": str(row_subject or "General"),
                "description": str(
                    description
                    or f"Study {topic_name}, make short notes, and practise questions."
                ),
                "estimated_hours": round(topic_hours, 2),
                "hours": round(topic_hours, 2),
                "completed": False,
            })

    # If there are no dataset matches, still give each selected subject
    # a useful starter step instead of returning an empty roadmap.
    if not roadmap:
        fallback_subjects = subjects or (
            ["Mathematics", "Science"]
            if str(class_level) == "10"
            else ["Mathematics", "Physics", "Chemistry"]
        )

        for subject in fallback_subjects:
            roadmap.append({
                "title": f"{subject} — revise key topics",
                "topic": f"{subject} — revise key topics",
                "subject": subject,
                "description": (
                    "Review your syllabus, make short notes, "
                    "and practise questions."
                ),
                "estimated_hours": school_topic_hours(subject, goal),
                "hours": school_topic_hours(subject, goal),
                "completed": False,
            })

    roadmap = roadmap[:30]
    total_hours = sum(item["estimated_hours"] for item in roadmap)
    weekly_hours = profile["weekly_learning_hours"]
    estimated_weeks = max(
        1, int((total_hours + weekly_hours - 1) // weekly_hours)
    )

    return {
        "roadmap": roadmap,
        "steps": roadmap,
        "total_hours": total_hours,
        "weekly_learning_hours": weekly_hours,
        "estimated_weeks": estimated_weeks,
        "goal": goal,
        "board": board,
        "class": class_level,
        "stream": profile["school_stream"],
    }


def recommend_school_resources(profile):
    resources = load_json("school_resources.json")

    board = profile["school_board"]
    class_level = profile["school_class"]
    subjects = {
        canonical_subject(subject)
        for subject in profile["school_subjects"]
    }

    matches = []
    seen_resources = set()

    for resource in resources:
        if not isinstance(resource, dict):
            continue

        resource_board = get_value(
            resource, "board", "education_board", "curriculum"
        )
        resource_class = get_value(
            resource, "class", "class_level", "grade", "standard"
        )
        resource_subject = normalize(
            get_value(resource, "subject", "subject_name")
        )
        title = str(
            get_value(resource, "title", "name", default="Learning resource")
        )
        url = str(get_value(resource, "url", "link", default="")).strip()

        if resource_board and not board_matches(resource_board, board):
            continue

        if resource_class and not class_matches(resource_class, class_level):
            continue

        # "All Subjects" and "General" resources apply to every subject.
        is_general = resource_subject in (
            "", "all subjects", "all subject", "general"
        )

        if subjects and resource_subject and not is_general:
            canonical_resource_subject = canonical_subject(resource_subject)
            if canonical_resource_subject not in subjects:
                continue

        # The same URL can serve several subjects (for example the NCERT
        # textbook page), so duplicates are checked per subject.
        resource_key = (url, canonical_subject(resource_subject))

        if not url or resource_key in seen_resources:
            continue

        seen_resources.add(resource_key)
        matches.append({
            "title": title,
            "name": title,
            "url": url,
            "subject": resource_subject.title() if resource_subject else "General",
            "board": resource_board or board,
            "class": resource_class or class_level,
            "type": get_value(resource, "type", default="learning"),
            "language": get_value(resource, "language", default=""),
            "free": resource.get("free", True),
        })

    return matches[:20]


def analyze_school(student_profile):
    board = get_value(
        student_profile, "school_board", "education_board", "board"
    )
    class_level = get_value(
        student_profile,
        "school_class", "current_class", "class_level", "grade"
    )
    stream = get_value(
        student_profile, "school_stream", "stream", "group", default="General"
    )
    subjects = as_list(
        get_value(student_profile, "school_subjects", "subjects")
    )
    goal = get_value(
        student_profile, "school_goal", "learning_goal", "goal",
        default="School Exams"
    )

    missing = []
    if not board:
        missing.append("school_board")
    if not class_level:
        missing.append("school_class")

    if missing:
        return {
            "success": False,
            "error": "Missing required school fields: " + ", ".join(missing),
        }, 400

    try:
        weekly_hours = float(get_value(
            student_profile,
            "weekly_learning_hours",
            "study_hours",
            "study_hours_per_week",
            default=5,
        ))

        if weekly_hours <= 0:
            raise ValueError

    except (ValueError, TypeError):
        return {
            "success": False,
            "error": "Study hours per week must be a valid positive number.",
        }, 400

    profile = {
        "student_name": get_value(
            student_profile, "student_name", "name", default="Student"
        ),
        "education_stage": "school",
        "school_board": str(board),
        "school_class": str(class_level),
        "school_stream": str(stream or "General"),
        "school_subjects": subjects,
        "school_goal": str(goal),
        "weekly_learning_hours": weekly_hours,
        "learning_style": get_value(
            student_profile, "learning_style", default="Mixed Learning"
        ),
    }

    roadmap_result = build_school_roadmap(profile)
    resources = recommend_school_resources(profile)

    study_plan = build_school_study_plan(
        roadmap_result["roadmap"], weekly_hours, goal
    )
    plan_weeks = max((item["week"] for item in study_plan), default=0)
    plan_hours = round(sum(item["hours"] for item in study_plan), 2)
    roadmap_result["estimated_weeks"] = plan_weeks

    school_summary = (
        f"Learning plan for Class {profile['school_class']} "
        f"({profile['school_board']}). Goal: {profile['school_goal']}. "
        f"Your roadmap contains {len(roadmap_result['roadmap'])} topics "
        f"and takes about {plan_weeks} weeks at "
        f"{format_hours(weekly_hours)} per week."
    )

    return {
        "success": True,
        "education_stage": "school",
        "profile_analysis": {
            "summary": school_summary,
            "readiness_score": None,
        },
        "school_profile": profile,
        "school_analysis": {
            "summary": school_summary,
            "board": profile["school_board"],
            "class": profile["school_class"],
            "stream": profile["school_stream"],
            "subjects": profile["school_subjects"],
            "goal": profile["school_goal"],
        },
        "school_roadmap": roadmap_result,
        "school_learning_roadmap": roadmap_result,
        "learning_roadmap": roadmap_result,
        "school_resources": resources,
        "school_resource_recommendations": resources,
        "resource_recommendations": {"resources": resources},
        "school_study_plan": study_plan,
        "study_plan": {
            "study_plan": study_plan,
            "days": study_plan,
            "total_planned_hours": plan_hours,
            "estimated_weeks": plan_weeks,
            "weekly_learning_hours": weekly_hours,
        },
    }, 200


@app.route("/", methods=["GET"])
def home():
    return app.send_static_file("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "message": "EduPath AI backend is healthy",
    })


@app.route("/api/careers", methods=["GET"])
def get_careers():
    careers = load_csv("careers_dataset.csv")
    career_list = []

    for _, row in careers.iterrows():
        career_list.append({
            "career_id": str(row.get("career_id", "")),
            "career_name": str(row.get("career_name", "")),
            "department": str(row.get("department", "")),
            "description": str(row.get("description", "")),
        })

    return jsonify({
        "success": True,
        "count": len(career_list),
        "careers": career_list,
    })


def predict_careers_hybrid(profile, top_n=3, ml_weight=0.6, department_boost=1.25):
    """Blend the trained ML model with TF-IDF text similarity.

    - The target career is NOT used for ranking (so AI suggestions stay honest);
      its rank and match are reported separately as "target_career_match".
    - Careers of the student's own department get a small boost.
    - If the ML model is unavailable, falls back to the old TF-IDF predictor.
    """
    if not ml_career_predictor.available:
        return career_predictor.predict_careers(profile, top_n=top_n)

    try:
        ml_result = ml_career_predictor.predict_careers(profile, top_n=100)
    except Exception:
        app.logger.exception("ML career prediction failed; using TF-IDF fallback")
        return career_predictor.predict_careers(profile, top_n=top_n)

    text_result = career_predictor.predict_careers(
        {**profile, "career_goal": ""}, top_n=100
    )

    ml_scores = {
        row["career_name"]: row["similarity_score"]
        for row in ml_result["recommendations"]
    }
    text_rows = text_result["recommendations"]
    text_total = sum(row["similarity_score"] for row in text_rows) or 1.0
    department = str(profile.get("department", "")).strip().upper()

    ranked = []
    for row in text_rows:
        name = row["career_name"]
        score = (
            ml_weight * ml_scores.get(name, 0.0)
            + (1 - ml_weight) * (row["similarity_score"] / text_total)
        )
        if str(row["department"]).strip().upper() == department:
            score *= department_boost
        ranked.append({
            **row,
            "ml_probability": round(ml_scores.get(name, 0.0), 4),
            "text_similarity": row["similarity_score"],
            "_score": score,
        })

    total = sum(item["_score"] for item in ranked) or 1.0
    for item in ranked:
        share = round(item.pop("_score") / total, 4)
        item["similarity_score"] = share
        item["prediction_score"] = share
        item["match_percent"] = round(share * 100, 1)
    ranked.sort(key=lambda item: item["match_percent"], reverse=True)

    target_name = str(profile.get("career_goal", "")).strip().lower()
    target_match = None
    for position, item in enumerate(ranked, start=1):
        if item["career_name"].lower() == target_name:
            target_match = {
                "career_name": item["career_name"],
                "rank": position,
                "total_careers": len(ranked),
                "match_percent": item["match_percent"],
            }
            break

    return {
        "success": True,
        "method": "Hybrid: Random Forest ML + TF-IDF + department boost",
        "recommendations": ranked[:max(1, int(top_n))],
        "target_career_match": target_match,
    }


@app.route("/api/analyze", methods=["POST"])
def analyze_student():
    student_profile = request.get_json(silent=True)

    if not isinstance(student_profile, dict):
        return jsonify({
            "success": False,
            "error": "Request body must contain a valid JSON object.",
        }), 400

    stage = normalize(get_value(
        student_profile, "education_stage", "educationStage", "stage"
    ))

    if stage in ("school", "school student", "school_student"):
        try:
            response, status_code = analyze_school(student_profile)
            return jsonify(response), status_code
        except Exception:
            app.logger.exception("School analysis failed")
            return jsonify({
                "success": False,
                "error": "School analysis failed. Check the backend terminal for details.",
            }), 500

    # Existing college analysis
    try:
        profile_result = profile_analyzer.analyze_profile(student_profile)
        analyzed_profile = profile_result["profile"]

        career_result = predict_careers_hybrid(analyzed_profile, top_n=3)

        requested_career = analyzed_profile["career_goal"]

        try:
            selected_career = skill_gap_analyzer.get_career_requirements(
                requested_career
            )
        except ValueError:
            recommendations = career_result.get("recommendations", [])
            if not recommendations:
                raise ValueError(
                    "No suitable career predictions were returned."
                )
            selected_career = skill_gap_analyzer.get_career_requirements(
                recommendations[0]["career_name"]
            )

        skill_gap_result = skill_gap_analyzer.analyze_skill_gaps(
            analyzed_profile, selected_career
        )

        known_skills = [
            {**item, "skill": skill_gap_analyzer.canonical_skill(item["skill"])}
            for item in analyzed_profile["current_skills"]
        ]

        roadmap_result = roadmap_generator.generate_roadmap(
            missing_skills=skill_gap_result["missing_skills"],
            weekly_learning_hours=analyzed_profile["weekly_learning_hours"],
            current_skills=known_skills,
        )

        resource_result = resource_recommender.recommend_resources(
            roadmap_result["roadmap"], max_per_skill=3
        )

        study_plan_result = study_planner.generate_study_plan(
            roadmap_result["roadmap"],
            weekly_learning_hours=analyzed_profile["weekly_learning_hours"],
        )

        return jsonify({
            "success": True,
            "education_stage": stage or "college",
            "profile_analysis": {
                "summary": profile_result["summary"],
                "readiness_score": profile_result["readiness_score"],
            },
            "career_predictions": career_result,
            "selected_career": selected_career["career_name"],
            "skill_gap_analysis": skill_gap_result,
            "learning_roadmap": roadmap_result,
            "resource_recommendations": resource_result,
            "study_plan": study_plan_result,
        })

    except (ValueError, KeyError, TypeError) as error:
        return jsonify({
            "success": False,
            "error": str(error),
        }), 400

    except Exception:
        app.logger.exception("Unexpected error during student analysis")
        return jsonify({
            "success": False,
            "error": "An unexpected server error occurred.",
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)