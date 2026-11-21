"""Module 3 - dictionary based skill extraction, categories and section detection."""
import re
from collections import defaultdict

import pandas as pd

SECTION_KEYWORDS = {
    "Education": ["education", "academic", "qualification"],
    "Skills": ["skills", "technical skills", "technologies", "tools"],
    "Projects": ["projects", "project work"],
    "Experience": ["experience", "internship", "work history", "employment"],
}


def load_skill_dictionary(path) -> pd.DataFrame:
    df = pd.read_csv(path, keep_default_na=False)
    df["aliases"] = df["aliases"].astype(str)
    return df


def _compile(df: pd.DataFrame) -> dict:
    patterns = {}
    for _, row in df.iterrows():
        names = {row["skill"].lower()} | {a.strip().lower() for a in row["aliases"].split("|") if a.strip()}
        alt = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
        # boundaries that do not split c++, c#, .net, node.js
        patterns[row["skill"]] = re.compile(rf"(?<![a-z0-9+#])(?:{alt})(?![a-z0-9+#])")
    return patterns


def extract_skills(clean: str, df: pd.DataFrame) -> dict:
    """Return {skill: mention_count} for every dictionary skill found."""
    found = {}
    for skill, pat in _compile(df).items():
        n = len(pat.findall(clean))
        if n:
            found[skill] = n
    return found


def group_by_category(found: dict, df: pd.DataFrame) -> dict:
    cat = dict(zip(df["skill"], df["category"]))
    grouped = defaultdict(list)
    for skill in found:
        grouped[cat.get(skill, "Other")].append(skill)
    return {k: sorted(v) for k, v in grouped.items()}


def detect_sections(raw_text: str) -> dict:
    """Which of education / skills / projects / experience headings exist."""
    lines = [l.strip().lower().rstrip(":") for l in raw_text.splitlines() if 0 < len(l.strip()) < 40]
    return {name: any(k in line for line in lines for k in kws) for name, kws in SECTION_KEYWORDS.items()}
