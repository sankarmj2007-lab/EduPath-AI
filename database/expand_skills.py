
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SKILLS_FILE = BASE_DIR / "skills_dataset.csv"

NEW_SKILLS = [
    {
        "skill_id": "S041",
        "skill_name": "Mathematics",
        "category": "Mathematics",
        "level": "Beginner",
        "prerequisites": "",
        "related_careers": "AI Engineer;Data Scientist;DSP Engineer;Communication Systems Engineer",
        "estimated_hours": 30,
    },
    {
        "skill_id": "S042",
        "skill_name": "Boolean Algebra",
        "category": "Digital Electronics",
        "level": "Beginner",
        "prerequisites": "Digital Electronics",
        "related_careers": "Digital Design Engineer;FPGA Design Engineer;VLSI Design Engineer",
        "estimated_hours": 15,
    },
    {
        "skill_id": "S043",
        "skill_name": "Analog Electronics",
        "category": "Electronics",
        "level": "Beginner",
        "prerequisites": "Digital Electronics",
        "related_careers": "Analog Design Engineer;PCB Design Engineer",
        "estimated_hours": 25,
    },
    {
        "skill_id": "S044",
        "skill_name": "Circuit Analysis",
        "category": "Electronics",
        "level": "Beginner",
        "prerequisites": "Mathematics",
        "related_careers": "Analog Design Engineer;PCB Design Engineer",
        "estimated_hours": 25,
    },
    {
        "skill_id": "S045",
        "skill_name": "Signals and Systems",
        "category": "ECE",
        "level": "Intermediate",
        "prerequisites": "Mathematics",
        "related_careers": "DSP Engineer;Communication Systems Engineer",
        "estimated_hours": 35,
    },
    {
        "skill_id": "S046",
        "skill_name": "Digital Signal Processing",
        "category": "ECE",
        "level": "Intermediate",
        "prerequisites": "Signals and Systems",
        "related_careers": "DSP Engineer",
        "estimated_hours": 40,
    },
    {
        "skill_id": "S047",
        "skill_name": "Communication Systems",
        "category": "ECE",
        "level": "Intermediate",
        "prerequisites": "Mathematics;Signals and Systems",
        "related_careers": "Communication Systems Engineer",
        "estimated_hours": 35,
    },
    {
        "skill_id": "S048",
        "skill_name": "Computer Networks",
        "category": "Networking",
        "level": "Beginner",
        "prerequisites": "Linux Basics",
        "related_careers": "Computer Networks Engineer;Cybersecurity Analyst;Cloud Engineer",
        "estimated_hours": 30,
    },
    {
        "skill_id": "S049",
        "skill_name": "Database Management",
        "category": "Database",
        "level": "Beginner",
        "prerequisites": "SQL",
        "related_careers": "Database Administrator;Backend Developer",
        "estimated_hours": 25,
    },
    {
        "skill_id": "S050",
        "skill_name": "MATLAB",
        "category": "Programming",
        "level": "Beginner",
        "prerequisites": "Mathematics",
        "related_careers": "DSP Engineer;Communication Systems Engineer",
        "estimated_hours": 25,
    },
    {
        "skill_id": "S051",
        "skill_name": "FPGA",
        "category": "Digital Design",
        "level": "Intermediate",
        "prerequisites": "Digital Electronics;Verilog",
        "related_careers": "FPGA Design Engineer;Digital Design Engineer",
        "estimated_hours": 35,
    },
    {
        "skill_id": "S052",
        "skill_name": "ASIC Design",
        "category": "VLSI",
        "level": "Advanced",
        "prerequisites": "Digital Electronics;CMOS Design",
        "related_careers": "ASIC Verification Engineer;VLSI Design Engineer",
        "estimated_hours": 50,
    },
    {
        "skill_id": "S053",
        "skill_name": "Static Timing Analysis",
        "category": "VLSI",
        "level": "Advanced",
        "prerequisites": "Digital Electronics;ASIC Design",
        "related_careers": "ASIC Verification Engineer;VLSI Design Engineer",
        "estimated_hours": 35,
    },
    {
        "skill_id": "S054",
        "skill_name": "Computer Architecture",
        "category": "Computer Engineering",
        "level": "Intermediate",
        "prerequisites": "Digital Electronics",
        "related_careers": "Digital Design Engineer;FPGA Design Engineer",
        "estimated_hours": 30,
    },
    {
        "skill_id": "S055",
        "skill_name": "PCB Design",
        "category": "Electronics",
        "level": "Intermediate",
        "prerequisites": "Circuit Analysis;Digital Electronics",
        "related_careers": "PCB Design Engineer",
        "estimated_hours": 30,
    },
    {
        "skill_id": "S056",
        "skill_name": "CMOS",
        "category": "VLSI",
        "level": "Intermediate",
        "prerequisites": "Digital Electronics",
        "related_careers": "Analog Design Engineer;VLSI Design Engineer",
        "estimated_hours": 30,
    },
]


def main():
    if not SKILLS_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {SKILLS_FILE}")

    df = pd.read_csv(SKILLS_FILE, keep_default_na=False)

    required_columns = [
        "skill_id", "skill_name", "category", "level",
        "prerequisites", "related_careers", "estimated_hours",
    ]

    if list(df.columns) != required_columns:
        raise ValueError(f"Unexpected columns: {df.columns.tolist()}")

    existing_ids = set(df["skill_id"].astype(str))
    existing_names = {
        name.strip().casefold()
        for name in df["skill_name"].astype(str)
    }

    additions = []

    for skill in NEW_SKILLS:
        skill_id = skill["skill_id"]
        skill_name = skill["skill_name"]

        if skill_id in existing_ids:
            print(f"Skipping existing ID: {skill_id}")
            continue

        if skill_name.casefold() in existing_names:
            print(f"Skipping existing skill: {skill_name}")
            continue

        additions.append(skill)
        existing_ids.add(skill_id)
        existing_names.add(skill_name.casefold())

    if additions:
        new_df = pd.DataFrame(additions, columns=required_columns)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(SKILLS_FILE, index=False, encoding="utf-8")

    print("Skill expansion completed.")
    print("New skills added:", len(additions))
    print("Total skills:", len(df))
    print("Unique skill IDs:", df["skill_id"].nunique())
    print("Unique skill names:", df["skill_name"].str.strip().str.casefold().nunique())


if __name__ == "__main__":
    main()
