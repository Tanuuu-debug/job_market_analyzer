import pandas as pd
import matplotlib.pyplot as plt
import ast
from collections import Counter


# Load datasets
df = pd.read_csv("data/cleaned_postings.csv")
skills_df = pd.read_csv("data/jobs_with_skills.csv")

print("Dataset loaded successfully!")
print("Total job postings:", len(df))


# ==========================================
# 1. DEFINE ANALYTICS / DATA ROLES
# ==========================================

analytics_keywords = [
    "data analyst",
    "data scientist",
    "business analyst",
    "business intelligence analyst",
    "business intelligence developer",
    "data engineer",
    "machine learning engineer",
    "machine learning scientist",
    "analytics engineer",
    "data analytics",
    "data science"
]


# Convert title to lowercase
df["title_lower"] = df["title"].str.lower()


# Find postings containing analytics-related titles
analytics_df = df[
    df["title_lower"].apply(
        lambda title: any(keyword in title for keyword in analytics_keywords)
    )
].copy()


print("\n===== ANALYTICS / DATA JOBS =====")
print("Number of analytics-related postings:", len(analytics_df))


# ==========================================
# 2. JOB ROLE COUNTS
# ==========================================

role_counts = analytics_df["title"].value_counts().head(15)

print("\n===== TOP ANALYTICS / DATA JOB TITLES =====")

for role, count in role_counts.items():
    print(f"{role}: {count}")


plt.figure(figsize=(10, 6))

plt.barh(
    role_counts.index[::-1],
    role_counts.values[::-1]
)

plt.xlabel("Number of Job Postings")
plt.ylabel("Job Title")
plt.title("Top Data & Analytics Job Titles")

plt.tight_layout()

plt.savefig("data/analytics_job_titles.png")

plt.show()


# ==========================================
# 3. EXPERIENCE LEVELS
# ==========================================

experience_counts = (
    analytics_df["formatted_experience_level"]
    .value_counts()
)

print("\n===== ANALYTICS JOB EXPERIENCE LEVELS =====")

for level, count in experience_counts.items():
    print(f"{level}: {count}")


# ==========================================
# 4. WORK TYPES
# ==========================================

work_counts = (
    analytics_df["formatted_work_type"]
    .value_counts()
)

print("\n===== ANALYTICS JOB WORK TYPES =====")

for work_type, count in work_counts.items():
    print(f"{work_type}: {count}")


# ==========================================
# 5. REMOTE JOBS
# ==========================================

remote_counts = analytics_df["remote_allowed"].value_counts(
    dropna=False
)

print("\n===== ANALYTICS JOB REMOTE STATUS =====")

print(remote_counts)


# ==========================================
# 6. TOP SKILLS FOR ANALYTICS JOBS
# ==========================================

# Match analytics job IDs with skill dataset
analytics_ids = set(analytics_df["job_id"])

analytics_skills_df = skills_df[
    skills_df["job_id"].isin(analytics_ids)
].copy()


analytics_skills_df["extracted_skills"] = (
    analytics_skills_df["extracted_skills"]
    .apply(
        lambda x: ast.literal_eval(x)
        if isinstance(x, str)
        else []
    )
)


skill_counter = Counter()

for skills in analytics_skills_df["extracted_skills"]:
    skill_counter.update(skills)


top_analytics_skills = skill_counter.most_common(15)


print("\n===== TOP SKILLS FOR DATA / ANALYTICS JOBS =====")

for skill, count in top_analytics_skills:
    print(f"{skill}: {count}")


# ==========================================
# 7. SKILL CHART
# ==========================================

skills = [
    item[0]
    for item in top_analytics_skills
]

counts = [
    item[1]
    for item in top_analytics_skills
]


plt.figure(figsize=(10, 6))

plt.barh(
    skills[::-1],
    counts[::-1]
)

plt.xlabel("Number of Job Postings")
plt.ylabel("Skill")
plt.title("Top Skills in Data & Analytics Jobs")

plt.tight_layout()

plt.savefig("data/analytics_skills.png")

plt.show()


print("\n========================================")
print("DATA & ANALYTICS ANALYSIS COMPLETED!")
print("========================================")