"""Generate anonymised sample resumes (DOCX) for testing."""
import docx
from pathlib import Path

SAMPLES = {
 "resume_a": ["Candidate A", "Education", "B.Sc. Statistics, 2023",
   "Skills", "Python, SQL, Excel, Pandas, Power BI, Tableau, Matplotlib, Data Visualization, Statistics",
   "Projects", "Sales dashboard in Power BI and Tableau. Cleaned data with Pandas and SQL.",
   "Experience", "Data analyst intern: built Excel reports and used statistical analysis."],
 "resume_b": ["Candidate B", "Education", "B.Tech Computer Science, 2024",
   "Skills", "Python, Machine Learning, scikit-learn, Pandas, FastAPI, Docker, MLflow, Git, AWS",
   "Projects", "Churn model built with scikit-learn and tracked in MLflow. Deployed ML model with FastAPI and Docker.",
   "Experience", "ML intern: model deployment and experiment tracking."],
 "resume_c": ["Candidate C", "Education", "M.Sc. Computational Linguistics, 2024",
   "Skills", "Python, NLP, Transformers, Hugging Face, spaCy, NLTK, PyTorch, BERT, LLM",
   "Projects", "Fine-tuned BERT with Hugging Face for sentiment analysis. NER pipeline in spaCy.",
   "Experience", "NLP research intern working on text classification."],
}
out = Path(__file__).parent / "sample_resumes"
out.mkdir(exist_ok=True)
for name, lines in SAMPLES.items():
    d = docx.Document()
    for l in lines:
        d.add_paragraph(l)
    d.save(out / f"{name}.docx")
print("created", list(SAMPLES))
