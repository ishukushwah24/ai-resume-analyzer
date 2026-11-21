"""Modules 4, 5, 6 - role dataset, TF-IDF + cosine matching, skill-gap analysis.

Match score = 70% required-skill coverage + 30% TF-IDF cosine similarity
(skills are tokens, so rarer skills such as MLflow weigh more than Python).
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

COVERAGE_WEIGHT = 0.7
COSINE_WEIGHT = 0.3


def load_roles(path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["skills_list"] = df["required_skills"].apply(lambda s: [x.strip() for x in s.split("|")])
    return df


def _tok(skills) -> str:
    return " ".join(s.lower().replace(" ", "_") for s in skills)


def match_roles(found_skills, roles_df: pd.DataFrame) -> pd.DataFrame:
    """Score the resume against every role; returns roles ranked best-first."""
    found = set(found_skills)
    role_docs = [_tok(s) for s in roles_df["skills_list"]]
    vec = TfidfVectorizer(token_pattern=r"\S+", lowercase=False)
    role_matrix = vec.fit_transform(role_docs)
    resume_vec = vec.transform([_tok(found)])
    cos = cosine_similarity(resume_vec, role_matrix)[0]

    rows = []
    for (_, r), c in zip(roles_df.iterrows(), cos):
        req = r["skills_list"]
        matched = [s for s in req if s in found]
        missing = [s for s in req if s not in found]
        coverage = len(matched) / len(req)
        score = 100 * (COVERAGE_WEIGHT * coverage + COSINE_WEIGHT * c)
        rows.append({"role": r["role"], "score": round(score, 1), "coverage": round(coverage * 100, 1),
                     "similarity": round(c * 100, 1), "matched": matched, "missing": missing})
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)


def skill_gap(role_row, counts: dict) -> dict:
    """Skills present, missing, and weak (mentioned only once) for one role."""
    weak = [s for s in role_row["matched"] if counts.get(s, 0) == 1]
    return {"found": role_row["matched"], "missing": role_row["missing"], "weak": weak}
