"""Module 6 - rule-based learning roadmap and downloadable report."""
from datetime import date

DISCLAIMER = ("Match scores are estimates based on keyword and skill overlap, not recruiter decisions. "
              "A missing keyword does not always mean missing ability. Use this tool for guidance only.")


def build_roadmap(missing, weak, skills_df, max_weeks: int = 6):
    """One missing skill per week (paired up if there are many), then weak-skill practice."""
    tasks = dict(zip(skills_df["skill"], skills_df["roadmap_task"]))
    topics = list(missing)
    per_week = 1 if len(topics) <= max_weeks else 2
    weeks = []
    for i in range(0, len(topics), per_week):
        chunk = topics[i:i + per_week]
        weeks.append({"week": f"Week {len(weeks) + 1}", "skills": chunk,
                      "tasks": [tasks.get(s, f"Learn the basics of {s} and build a mini project") for s in chunk]})
    if weak:
        weeks.append({"week": f"Week {len(weeks) + 1}", "skills": list(weak),
                      "tasks": [f"Strengthen {', '.join(weak)}: add them to a project and your resume with evidence"]})
    if topics:
        weeks.append({"week": f"Week {len(weeks) + 1}", "skills": topics,
                      "tasks": [f"Capstone: build and publish one project using {', '.join(topics[:3])}"]})
    return weeks


def build_report(filename, role, score, found_counts, grouped, ranked, gap, roadmap, sections) -> str:
    L = [f"# Resume Analysis Report", f"_Generated {date.today().isoformat()} for `{filename}`_", "",
         f"**Target Role:** {role}", f"**Resume Match Score:** {score}%", "", "## Skills Found"]
    for cat, skills in grouped.items():
        L.append(f"- **{cat}:** {', '.join(skills)}")
    L += ["", "## Resume Sections Detected"] + [f"- {k}: {'yes' if v else 'not found'}" for k, v in sections.items()]
    L += ["", "## Missing Skills"] + ([f"- {s}" for s in gap["missing"]] or ["- None. All required skills found."])
    if gap["weak"]:
        L += ["", "## Weak Skills (mentioned once)"] + [f"- {s}" for s in gap["weak"]]
    L += ["", "## Recommended Roles"]
    for i, r in ranked.head(3).iterrows():
        L.append(f"{i + 1}. {r['role']} - {r['score']}%")
    L += ["", "## Suggested Roadmap"]
    for w in roadmap:
        L.append(f"- **{w['week']}** ({', '.join(w['skills'])}): {'; '.join(w['tasks'])}")
    L += ["", "---", DISCLAIMER]
    return "\n".join(L)
