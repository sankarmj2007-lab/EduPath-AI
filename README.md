# EduPath AI
    🔗 **Live Demo:** https://edupath-ai-7hv0.onrender.com
    
AI-powered education and career guidance platform.
Final project of the IBM online internship.

EduPath AI analyzes a student's profile and gives personalized career
predictions, a skill gap analysis, a learning roadmap, learning resources,
a weekly study plan, and a downloadable PDF report.

## Features

- Student profile analysis (school, college, graduate, working professional)
- Career prediction with a trained Random Forest model (top 3 careers)
- Target career match (rank among 30 careers)
- Skill gap analysis against career requirements
- Personalized learning roadmap with prerequisites and estimated hours
- Learning resource recommendations
- Week-by-week study plan based on available study hours
- Download the full page as a PDF report

## Technology Stack

| Part | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| AI / ML | scikit-learn (Random Forest), TF-IDF, pandas, NumPy |
| Data | CSV and JSON files |

## How the AI Works

Career prediction is hybrid:

1. A Random Forest model trained on 3,000 synthetic student profiles
   (30 careers, 89 features such as skills, interests, assessment scores,
   CGPA and projects).
2. TF-IDF text similarity between the profile and career descriptions.
3. A small boost for careers of the student's own department.

The target career chosen by the student is NOT used for ranking. Its rank is
shown separately. If the trained model is missing, the app falls back to
TF-IDF automatically.

### Model results (synthetic data, 80/20 split)

| Metric | Value |
|---|---|
| Top-1 accuracy | 43.7% |
| Top-3 accuracy | 80.7% |
| Top-5 accuracy | 92.2% |
| Macro F1 | 0.445 |
| 5-fold CV top-1 | 41.3% (+/- 2.2%) |

The platform shows the top 3 careers, so top-3 accuracy matters most.
The training data is synthetic, so these numbers must be validated on real
student responses.

## Project Structure

```
EduPath-AI-v2/
  ai/          AI modules (profile, skill gap, career model, roadmap, ...)
  backend/     Flask API (app.py)
  database/    Datasets and the synthetic dataset generator
  frontend/    index.html, script.js, CSS files, print.css
  model/       Trained model and evaluation files
  requirements.txt
```

## Setup and Run (Windows PowerShell)

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python backend/app.py
```

The backend runs at http://127.0.0.1:5000.
Then open `frontend/index.html` in Chrome or Edge, fill the form and click
"Analyze My Profile". Use "Download PDF" and choose "Save as PDF".

### Retrain the model (optional)

```
python database/generate_student_profiles.py
python ai/career_model.py train
python ai/career_model.py demo
```

## Limitations

- Training data is synthetic.
- The current form collects limited data, so match scores are modest.

## Future Scope

- Step-by-step profile wizard with skill levels and a short AI assessment
- Validation with real student data
- AI chat assistant
- User login and database
- Mock interviews and resume builder

## Author

Sankar M
