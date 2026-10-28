import pandas as pd
import ast
from collections import Counter
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data/jobs_with_skills.csv")

print("Dataset loaded successfully!")
print("Number of jobs:", len(df))


# Convert extracted_skills from text back into a Python list
df["extracted_skills"] = df["extracted_skills"].apply(
    lambda x: ast.literal_eval(x) if isinstance(x, str) else []
)


# Count all skills
skill_counter = Counter()

for skills in df["extracted_skills"]:
    skill_counter.update(skills)


# Get top 15 skills
top_skills = skill_counter.most_common(15)


print("\n===== TOP 15 IN-DEMAND SKILLS =====")

for skill, count in top_skills:
    print(f"{skill}: {count}")


# Create chart
skills = [item[0] for item in top_skills]
counts = [item[1] for item in top_skills]

plt.figure(figsize=(10, 6))

plt.barh(skills[::-1], counts[::-1])

plt.xlabel("Number of Job Postings")
plt.ylabel("Skills")
plt.title("Top 15 In-Demand Skills")

plt.tight_layout()

plt.savefig("data/top_skills.png")

plt.show()

print("\nChart saved to: data/top_skills.png")