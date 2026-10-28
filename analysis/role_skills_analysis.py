
import pandas as pd
import ast
import matplotlib.pyplot as plt
from collections import Counter

# Load job postings and extracted skills
df = pd.read_csv("data/jobs_with_skills.csv")

# Convert extracted skills into Python lists
df["extracted_skills"] = df["extracted_skills"].apply(
    lambda x: ast.literal_eval(x) if isinstance(x, str) else []
)

# Define the job roles we want to compare
roles = {
    "Data Analyst": ["data analyst"],
    "Data Scientist": ["data scientist"],
    "Business Analyst": ["business analyst"],
    "Data Engineer": ["data engineer"],
    "Machine Learning Engineer": ["machine learning engineer"]
}

results = []

for role_name, keywords in roles.items():

    # Find matching job postings
    mask = df["title"].fillna("").str.lower().apply(
        lambda title: any(keyword in title for keyword in keywords)
    )

    role_df = df[mask]

    print(f"\n===== {role_name} =====")
    print("Number of job postings:", len(role_df))

    # Count skills for this role
    counter = Counter()

    for skills in role_df["extracted_skills"]:
        counter.update(skills)

    # Display top 10 skills
    print("Top skills:")

    for skill, count in counter.most_common(10):
        print(f"{skill}: {count}")

    # Save skill counts for comparison
    for skill, count in counter.items():
        results.append({
            "role": role_name,
            "skill": skill,
            "count": count
        })

# Save results as a CSV file
results_df = pd.DataFrame(results)
results_df.to_csv(
    "data/role_skill_counts.csv",
    index=False
)

# Compare key analytics skills across roles
key_skills = [
    "python",
    "sql",
    "excel",
    "tableau",
    "power bi",
    "r",
    "statistics",
    "machine learning"
]

comparison = results_df[
    results_df["skill"].isin(key_skills)
]

if not comparison.empty:
    pivot = comparison.pivot_table(
        index="role",
        columns="skill",
        values="count",
        aggfunc="sum",
        fill_value=0
    )

    ax = pivot.plot(
        kind="bar",
        figsize=(12, 6)
    )

    ax.set_xlabel("Job Role")
    ax.set_ylabel("Number of Job Postings Mentioning Skill")
    ax.set_title("Skill Requirements Across Data Roles")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()

    plt.savefig("data/role_skill_comparison.png")
    plt.show()

print("\nRole-skill analysis completed!")
print("Saved: data/role_skill_counts.csv")
print("Saved: data/role_skill_comparison.png")
