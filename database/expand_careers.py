
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CAREERS_FILE = BASE_DIR / "careers_dataset.csv"

NEW_CAREERS = [
    ("C009", "Frontend Developer", "ALL",
     "HTML;CSS;JavaScript;Git;Problem Solving",
     "Beginner-to-Advanced",
     "Builds responsive and accessible website interfaces."),

    ("C010", "Backend Developer", "ALL",
     "Python;Flask;REST APIs;SQL;Git",
     "Beginner-to-Advanced",
     "Develops server-side applications, APIs and databases."),

    ("C011", "Full Stack Developer", "ALL",
     "HTML;CSS;JavaScript;Python;Flask;SQL;Git;REST APIs",
     "Beginner-to-Advanced",
     "Develops both frontend and backend web applications."),

    ("C012", "Mobile App Developer", "ALL",
     "JavaScript;Python;SQL;REST APIs;Git;OOP",
     "Beginner-to-Advanced",
     "Builds mobile applications and connects them to backend services."),

    ("C013", "Data Scientist", "ALL",
     "Python;Mathematics;Statistics;NumPy;Pandas;Scikit-learn;Data Visualization",
     "Beginner-to-Advanced",
     "Analyzes data and builds statistical and machine learning models."),

    ("C014", "Machine Learning Engineer", "ALL",
     "Python;Mathematics;Statistics;Scikit-learn;Machine Learning;SQL",
     "Beginner-to-Advanced",
     "Builds and deploys machine learning models."),

    ("C015", "Deep Learning Engineer", "ALL",
     "Python;Mathematics;Linear Algebra;Deep Learning;Machine Learning;NumPy",
     "Beginner-to-Advanced",
     "Develops neural networks for advanced AI applications."),

    ("C016", "Computer Vision Engineer", "ALL",
     "Python;Mathematics;Linear Algebra;Computer Vision;Deep Learning;NumPy",
     "Beginner-to-Advanced",
     "Develops systems that understand images and videos."),

    ("C017", "Cybersecurity Analyst", "ALL",
     "Linux Basics;Python;Computer Networks;Problem Solving;SQL",
     "Beginner-to-Advanced",
     "Monitors systems and investigates cybersecurity threats."),

    ("C018", "Cloud Engineer", "ALL",
     "Linux Basics;Python;Computer Networks;Git;REST APIs",
     "Beginner-to-Advanced",
     "Deploys and maintains applications in cloud environments."),

    ("C019", "DevOps Engineer", "ALL",
     "Linux Basics;Python;Git;REST APIs;Computer Networks",
     "Beginner-to-Advanced",
     "Automates software development and deployment workflows."),

    ("C020", "Database Administrator", "ALL",
     "SQL;Database Management;Linux Basics;Python",
     "Beginner-to-Advanced",
     "Maintains database security, performance and availability."),

    ("C021", "QA Automation Engineer", "ALL",
     "Python;JavaScript;Git;Problem Solving;OOP",
     "Beginner-to-Advanced",
     "Creates automated software tests to improve application quality."),

    ("C022", "Game Developer", "ALL",
     "C Programming;Python;OOP;Algorithms;Mathematics",
     "Beginner-to-Advanced",
     "Develops game mechanics and interactive software."),

    ("C023", "Computer Networks Engineer", "ECE",
     "Computer Networks;Communication Protocols;Linux Basics;Problem Solving",
     "Beginner-to-Advanced",
     "Designs and troubleshoots computer communication networks."),

    ("C024", "DSP Engineer", "ECE",
     "Mathematics;Signals and Systems;Python;MATLAB;Digital Signal Processing",
     "Beginner-to-Advanced",
     "Develops algorithms for digital signal processing."),

    ("C025", "Communication Systems Engineer", "ECE",
     "Mathematics;Signals and Systems;Communication Systems;Digital Electronics",
     "Beginner-to-Advanced",
     "Designs and analyzes communication systems."),

    ("C026", "Analog Design Engineer", "ECE",
     "CMOS;Analog Electronics;Circuit Analysis;Mathematics",
     "Beginner-to-Advanced",
     "Designs analog electronic circuits and integrated circuit blocks."),

    ("C027", "Digital Design Engineer", "ECE",
     "Digital Electronics;Boolean Algebra;Verilog;Computer Architecture",
     "Beginner-to-Advanced",
     "Designs digital logic circuits and RTL hardware modules."),

    ("C028", "FPGA Design Engineer", "ECE",
     "Digital Electronics;Verilog;SystemVerilog;FPGA;Computer Architecture",
     "Beginner-to-Advanced",
     "Implements digital hardware designs on FPGA devices."),

    ("C029", "ASIC Verification Engineer", "ECE",
     "Verilog;SystemVerilog;ASIC Design;Digital Electronics;Static Timing Analysis",
     "Beginner-to-Advanced",
     "Verifies integrated circuit designs for functional correctness."),

    ("C030", "PCB Design Engineer", "ECE",
     "Digital Electronics;Analog Electronics;Circuit Analysis;PCB Design",
     "Beginner-to-Advanced",
     "Creates PCB schematics, board layouts and design documentation."),
]


def main():
    if not CAREERS_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {CAREERS_FILE}")

    df = pd.read_csv(CAREERS_FILE, keep_default_na=False)

    required_columns = [
        "career_id", "career_name", "department",
        "required_skills", "skill_level", "description"
    ]

    if list(df.columns) != required_columns:
        raise ValueError(f"Unexpected columns: {df.columns.tolist()}")

    existing_ids = set(df["career_id"].astype(str))
    existing_names = {
        name.strip().casefold()
        for name in df["career_name"].astype(str)
    }

    additions = []

    for row in NEW_CAREERS:
        career_id, career_name = row[0], row[1]

        if career_id in existing_ids:
            print(f"Already exists, skipping ID: {career_id}")
            continue

        if career_name.casefold() in existing_names:
            print(f"Already exists, skipping: {career_name}")
            continue

        additions.append(row)
        existing_ids.add(career_id)
        existing_names.add(career_name.casefold())

    if additions:
        new_df = pd.DataFrame(additions, columns=required_columns)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(CAREERS_FILE, index=False, encoding="utf-8")

    print("Career expansion completed.")
    print("New careers added:", len(additions))
    print("Total careers:", len(df))
    print("Unique IDs:", df["career_id"].nunique())
    print("Unique names:", df["career_name"].str.casefold().nunique())


if __name__ == "__main__":
    main()
