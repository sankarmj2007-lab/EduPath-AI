
import json
from pathlib import Path

RESOURCE_FILE = Path(__file__).parent / "resources.json"

NEW_RESOURCES = [
    {
        "skill": "SystemVerilog",
        "type": "Course",
        "title": "SystemVerilog Academy - Free Learning Paths",
        "url": "https://www.systemverilogacademy.com/courses",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "VLSI Design",
        "type": "Tutorial",
        "title": "VLSI Mentor - Free Learning Library",
        "url": "https://www.vlsimentor.com/learnings",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Verilog",
        "type": "Course",
        "title": "AMD - Designing with Verilog",
        "url": "https://docs.amd.com/api/khub/documents/qfE334lSdsI980HYHNsHxA/content",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "FPGA Design",
        "type": "Tutorial",
        "title": "Altera FPGA Training Resources",
        "url": "https://docs.altera.com/",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "ASIC Verification",
        "type": "Tutorial",
        "title": "VLSI Mentor - Verification Learning",
        "url": "https://www.vlsimentor.com/learnings",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Cybersecurity",
        "type": "Course",
        "title": "Cisco Networking Academy",
        "url": "https://www.netacad.com/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Cybersecurity",
        "type": "Reference",
        "title": "NIST Free and Low-Cost Cybersecurity Learning",
        "url": "https://www.nist.gov/itl/applied-cybersecurity/nice/resources/online-learning-content",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Cloud Computing",
        "type": "Course",
        "title": "NIELIT Virtual Academy",
        "url": "https://lms.nielit.gov.in/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "DevOps",
        "type": "Course",
        "title": "Linux Foundation Learning Resources",
        "url": "https://training.linuxfoundation.org/resources/",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Computer Networks",
        "type": "Course",
        "title": "Cisco Networking Academy",
        "url": "https://www.netacad.com/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "SQL",
        "type": "Tutorial",
        "title": "PostgreSQL Official Documentation",
        "url": "https://www.postgresql.org/docs/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Data Science",
        "type": "Course",
        "title": "Kaggle Learn",
        "url": "https://www.kaggle.com/learn",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Machine Learning",
        "type": "Course",
        "title": "Google Machine Learning Education",
        "url": "https://developers.google.com/machine-learning",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Deep Learning",
        "type": "Tutorial",
        "title": "PyTorch Official Tutorials",
        "url": "https://docs.pytorch.org/tutorials/",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Computer Vision",
        "type": "Tutorial",
        "title": "OpenCV Official Tutorials",
        "url": "https://docs.opencv.org/",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Python Programming",
        "type": "Documentation",
        "title": "Official Python Tutorial",
        "url": "https://docs.python.org/3/tutorial/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "JavaScript",
        "type": "Documentation",
        "title": "MDN JavaScript Guide",
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Git",
        "type": "Tutorial",
        "title": "Git Official Book",
        "url": "https://git-scm.com/book/en/v2",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Embedded Systems",
        "type": "Documentation",
        "title": "ESP-IDF Programming Guide",
        "url": "https://docs.espressif.com/projects/esp-idf/en/stable/esp32/",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Robotics",
        "type": "Tutorial",
        "title": "ROS 2 Official Tutorials",
        "url": "https://docs.ros.org/en/jazzy/Tutorials.html",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Digital Signal Processing",
        "type": "Course",
        "title": "MIT OpenCourseWare",
        "url": "https://ocw.mit.edu/",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "MATLAB",
        "type": "Course",
        "title": "MATLAB Onramp",
        "url": "https://matlabacademy.mathworks.com/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "PCB Design",
        "type": "Documentation",
        "title": "KiCad Official Documentation",
        "url": "https://docs.kicad.org/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "REST APIs",
        "type": "Documentation",
        "title": "MDN - HTTP and Web APIs",
        "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Linux Basics",
        "type": "Course",
        "title": "Linux Foundation Learning Resources",
        "url": "https://training.linuxfoundation.org/resources/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    
    {
        "skill": "RTOS",
        "type": "documentation",
        "title": "FreeRTOS Official Documentation",
        "url": "https://www.freertos.org/Documentation/RTOS_book.html",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Embedded Linux",
        "type": "documentation",
        "title": "Yocto Project Documentation",
        "url": "https://docs.yoctoproject.org/",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Statistics",
        "type": "course",
        "title": "Khan Academy Statistics and Probability",
        "url": "https://www.khanacademy.org/math/statistics-probability",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Scikit-learn",
        "type": "documentation",
        "title": "Scikit-learn User Guide",
        "url": "https://scikit-learn.org/stable/user_guide.html",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "CMOS Design",
        "type": "course",
        "title": "NPTEL Online Courses",
        "url": "https://nptel.ac.in/courses",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Algorithms",
        "type": "course",
        "title": "MIT OpenCourseWare - Introduction to Algorithms",
        "url": "https://ocw.mit.edu/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Excel",
        "type": "tutorial",
        "title": "Microsoft Excel Help and Learning",
        "url": "https://support.microsoft.com/excel",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Data Visualization",
        "type": "tutorial",
        "title": "Tableau Free Training Videos",
        "url": "https://www.tableau.com/learn/training",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Power BI",
        "type": "documentation",
        "title": "Microsoft Power BI Learning",
        "url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Sensors",
        "type": "tutorial",
        "title": "Arduino Documentation",
        "url": "https://docs.arduino.cc/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Communication Protocols",
        "type": "documentation",
        "title": "Linux Foundation Networking Resources",
        "url": "https://training.linuxfoundation.org/resources/",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "MQTT",
        "type": "documentation",
        "title": "MQTT Official Documentation",
        "url": "https://mqtt.org/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Control Systems",
        "type": "course",
        "title": "NPTEL Control Systems Courses",
        "url": "https://nptel.ac.in/courses",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "ROS",
        "type": "tutorial",
        "title": "ROS 2 Official Tutorials",
        "url": "https://docs.ros.org/en/jazzy/Tutorials.html",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Problem Solving",
        "type": "practice",
        "title": "HackerRank Problem Solving",
        "url": "https://www.hackerrank.com/domains/algorithms",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Linear Algebra",
        "type": "course",
        "title": "Khan Academy Linear Algebra",
        "url": "https://www.khanacademy.org/math/linear-algebra",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Mathematics",
        "type": "course",
        "title": "Khan Academy Mathematics",
        "url": "https://www.khanacademy.org/math",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Boolean Algebra",
        "type": "tutorial",
        "title": "All About Circuits - Digital",
        "url": "https://www.allaboutcircuits.com/textbook/digital/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Analog Electronics",
        "type": "tutorial",
        "title": "All About Circuits - Semiconductors",
        "url": "https://www.allaboutcircuits.com/textbook/semiconductors/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Circuit Analysis",
        "type": "tutorial",
        "title": "All About Circuits - DC",
        "url": "https://www.allaboutcircuits.com/textbook/direct-current/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "Signals and Systems",
        "type": "course",
        "title": "NPTEL Signals and Systems Courses",
        "url": "https://nptel.ac.in/courses",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Communication Systems",
        "type": "course",
        "title": "NPTEL Communication Systems Courses",
        "url": "https://nptel.ac.in/courses",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Database Management",
        "type": "tutorial",
        "title": "PostgreSQL Official Documentation",
        "url": "https://www.postgresql.org/docs/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "FPGA",
        "type": "documentation",
        "title": "AMD FPGA Documentation",
        "url": "https://docs.amd.com/",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "ASIC Design",
        "type": "tutorial",
        "title": "VLSI Mentor Learning Resources",
        "url": "https://www.vlsimentor.com/learnings",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Static Timing Analysis",
        "type": "documentation",
        "title": "OpenSTA Documentation",
        "url": "https://github.com/The-OpenROAD-Project/OpenSTA",
        "level": "Intermediate",
        "language": "English",
        "free": True
    },
    {
        "skill": "Computer Architecture",
        "type": "course",
        "title": "Nand2Tetris",
        "url": "https://www.nand2tetris.org/",
        "level": "Beginner",
        "language": "English",
        "free": True
    },
    {
        "skill": "CMOS",
        "type": "course",
        "title": "NPTEL Online Courses",
        "url": "https://nptel.ac.in/courses",
        "level": "Intermediate",
        "language": "English",
        "free": True
    }

]


def main():
    if not RESOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Resource file not found: {RESOURCE_FILE}"
        )

    with RESOURCE_FILE.open("r", encoding="utf-8") as file:
        resources = json.load(file)

    if not isinstance(resources, list):
        raise ValueError("resources.json must contain a JSON list.")

    existing_ids = [
        int(item["resource_id"][1:])
        for item in resources
        if str(item.get("resource_id", "")).startswith("R")
        and str(item["resource_id"])[1:].isdigit()
    ]

    next_id = max(existing_ids, default=0) + 1
    existing_keys = {
        (
            item.get("skill", "").strip().lower(),
            item.get("title", "").strip().lower()
        )
        for item in resources
    }

    added = 0

    for item in NEW_RESOURCES:
        key = (
            item["skill"].strip().lower(),
            item["title"].strip().lower()
        )

        if key in existing_keys:
            continue

        new_item = {
            "resource_id": f"R{next_id:03d}",
            **item
        }

        resources.append(new_item)
        existing_keys.add(key)
        next_id += 1
        added += 1

    with RESOURCE_FILE.open("w", encoding="utf-8") as file:
        json.dump(resources, file, indent=2, ensure_ascii=False)
        file.write("\n")

    print("Resource expansion completed.")
    print("New resources added:", added)
    print("Total resources:", len(resources))


if __name__ == "__main__":
    main()
