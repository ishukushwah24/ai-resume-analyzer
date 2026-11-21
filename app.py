"""Module 7 - Streamlit dashboard for the AI Resume Analyzer and Job Recommendation System."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from job_matcher import load_roles, match_roles, skill_gap
from resume_parser import MAX_FILE_MB, ResumeError, extract_text
from roadmap_generator import DISCLAIMER, build_report, build_roadmap
from skill_extractor import detect_sections, extract_skills, group_by_category, load_skill_dictionary
from text_cleaner import clean_text

BASE = Path(__file__).parent
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")


@st.cache_data
def load_data():
    return load_skill_dictionary(BASE / "data" / "skill_dictionary.csv"), load_roles(BASE / "data" / "job_roles.csv")


skills_df, roles_df = load_data()

st.title("📄 AI Resume Analyzer & Job Recommendation System")
st.caption("Check how well your resume matches a job role, find skill gaps and get a learning roadmap.")

with st.sidebar:
    st.header("1. Upload resume")
    uploaded = st.file_uploader(f"PDF or DOCX (max {MAX_FILE_MB} MB)", type=["pdf", "docx"])
    st.header("2. Target role")
    target_role = st.selectbox("Choose a role", roles_df["role"].tolist())
    st.info("Your resume is processed in memory and is not stored. Contact details are removed before analysis.")

if uploaded is None:
    st.write("👈 Upload a resume to begin.")
    st.subheader("Roles covered")
    st.dataframe(roles_df[["role", "required_skills"]].rename(columns={"required_skills": "required skills (|)"}),
                 use_container_width=True, hide_index=True)
    st.stop()

# ---- pipeline: extract -> clean -> skills -> match -> gap -> roadmap ----
try:
    raw_text = extract_text(uploaded.name, uploaded.getvalue())
except ResumeError as err:
    st.error(str(err))
    st.stop()

st.success(f"Uploaded: **{uploaded.name}**")
clean = clean_text(raw_text)
counts = extract_skills(clean, skills_df)
grouped = group_by_category(counts, skills_df)
sections = detect_sections(raw_text)
ranked = match_roles(counts.keys(), roles_df)
target_row = ranked[ranked["role"] == target_role].iloc[0]
gap = skill_gap(target_row, counts)
roadmap = build_roadmap(gap["missing"], gap["weak"], skills_df)

if len(counts) < 5:
    st.warning("Very few skills detected. Check that the resume text was extracted properly or add a Skills section.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Recommended roles", "Skill gap", "Learning roadmap", "Download report"])

with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Match score: {target_role}", f"{target_row['score']}%")
    c2.metric("Skills detected", len(counts))
    c3.metric("Required skills found", f"{len(gap['found'])}/{len(target_row['matched']) + len(gap['missing'])}")
    st.progress(min(int(target_row["score"]), 100))
    st.subheader("Extracted skills")
    for cat, skills in grouped.items():
        st.markdown(f"**{cat}:** " + " ".join(f"`{s}`" for s in skills))
    st.subheader("Resume sections detected")
    cols = st.columns(4)
    for col, (name, ok) in zip(cols, sections.items()):
        col.write(("✅ " if ok else "⚠️ ") + name)
    st.caption(DISCLAIMER)

with tab2:
    st.subheader("Top 3 suitable roles")
    for i, r in ranked.head(3).iterrows():
        st.markdown(f"**{i + 1}. {r['role']}** - {r['score']}%  \n"
                    f"Matched {len(r['matched'])} of {len(r['matched']) + len(r['missing'])} required skills")
    fig = px.bar(ranked.sort_values("score"), x="score", y="role", orientation="h", text="score",
                 range_x=[0, 100], labels={"score": "Match score (%)", "role": ""}, title="Match score by role")
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("How is the score calculated?"):
        st.write("Score = 70% required-skill coverage + 30% TF-IDF cosine similarity between your skills "
                 "and the role's skills (rarer skills weigh more).")
        st.dataframe(ranked[["role", "score", "coverage", "similarity"]], hide_index=True, use_container_width=True)

with tab3:
    st.subheader(f"Skill gap for {target_role}")
    a, b, c = st.columns(3)
    a.markdown("**✅ Found**")
    [a.write(f"- {s}") for s in gap["found"]] or None
    b.markdown("**❌ Missing**")
    [b.write(f"- {s}") for s in gap["missing"]] or b.write("None 🎉")
    c.markdown("**⚠️ Weak (mentioned once)**")
    [c.write(f"- {s}") for s in gap["weak"]] or c.write("None")
    st.caption("A missing keyword does not always mean missing ability. Add evidence from projects if you have it.")

with tab4:
    st.subheader("Suggested roadmap")
    if not roadmap:
        st.success("You already cover every required skill for this role.")
    for w in roadmap:
        with st.container(border=True):
            st.markdown(f"**{w['week']}: {', '.join(w['skills'])}**")
            for t in w["tasks"]:
                st.write(f"- {t}")

with tab5:
    report = build_report(uploaded.name, target_role, target_row["score"], counts, grouped, ranked,
                          gap, roadmap, sections)
    st.markdown(report)
    st.download_button("⬇️ Download report (.md)", report, file_name="resume_analysis_report.md", mime="text/markdown")
    st.download_button("⬇️ Download scores (.csv)",
                       ranked[["role", "score", "coverage", "similarity"]].to_csv(index=False),
                       file_name="role_scores.csv", mime="text/csv")
