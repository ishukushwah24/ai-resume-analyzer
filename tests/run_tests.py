"""Fills the evaluation sheet: expected vs actual top role + score-consistency check."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from job_matcher import load_roles, match_roles
from resume_parser import extract_text
from skill_extractor import extract_skills, load_skill_dictionary
from text_cleaner import clean_text

skills_df = load_skill_dictionary(ROOT / "data/skill_dictionary.csv")
roles_df = load_roles(ROOT / "data/job_roles.csv")

# 1. Skill extraction on tricky symbols
tricky = clean_text("Experienced in C++, C#, .NET, Node.js, CI/CD and scikit-learn. Email: a@b.com Phone 9876543210")
found = extract_skills(tricky, skills_df)
assert {"C++", "C#", "Node.js", "CI/CD", "scikit-learn"} <= set(found), found
assert "a@b.com" not in tricky and "9876543210" not in tricky
print("OK  symbol handling + personal info removal")

# 2. Role ranking on sample resumes
cases = pd.read_csv(ROOT / "tests/test_cases.csv")
actual, comments = [], []
for _, row in cases.iterrows():
    path = ROOT / "sample_resumes" / row["test_resume"]
    counts = extract_skills(clean_text(extract_text(path.name, path.read_bytes())), skills_df)
    ranked = match_roles(counts.keys(), roles_df)
    top = ranked.iloc[0]["role"]
    actual.append(top)
    comments.append(f"{len(counts)} skills; top score {ranked.iloc[0]['score']}%; " + ("PASS" if top == row["expected_top_role"] else "CHECK"))
cases["actual_top_role"], cases["comments"] = actual, comments
cases.to_csv(ROOT / "tests/evaluation_sheet.csv", index=False)
print(cases.to_string(index=False))

# 3. Score consistency: adding a required skill must not lower the score
base = match_roles(["Python", "SQL"], roles_df).set_index("role").loc["Data Analyst", "score"]
more = match_roles(["Python", "SQL", "Excel"], roles_df).set_index("role").loc["Data Analyst", "score"]
assert more > base, (base, more)
print(f"OK  score consistency ({base} -> {more})")
assert all(a == e for a, e in zip(actual, cases["expected_top_role"])), "ranking mismatch"
print("ALL TESTS PASSED")
