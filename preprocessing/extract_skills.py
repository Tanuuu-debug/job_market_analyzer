
import pandas as pd
import re
from collections import Counter

from analysis.skills import SKILLS


# ==========================================
# 1. LOAD CLEANED DATASET
# ==========================================

df = pd.read_csv("data/cleaned_postings.csv")

print("Starting skill extraction...")
print("Number of job descriptions:", len(df))


# ==========================================
# 2. SKILL EXTRACTION FUNCTION
# ==========================================

def extract_skills(text):

    if not isinstance(text, str):
        return []

    text = text.lower()

    found_skills = []

    for skill in SKILLS:

        skill_lower = skill.lower()

        # Special handling for short or symbol-based skill names
        if skill_lower == "r":
            # Match R as a standalone term
            pattern = r"(?<!\w)r(?!\w)"

        elif skill_lower == "c":
            # Match C as a standalone term
            pattern = r"(?<!\w)c(?!\w)"

        elif skill_lower == "go":
            # Match Go as a standalone term
            pattern = r"(?<!\w)go(?!\w)"

        elif skill_lower in ["c++", "c#", "node.js"]:
            pattern = re.escape(skill_lower)

        else:
            # Match complete skill names, not parts of other words
            pattern = r"(?<!\w)" + re.escape(skill_lower) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills


# ==========================================
# 3. EXTRACT SKILLS
# ==========================================

df["extracted_skills"] = df["description"].apply(extract_skills)


# ==========================================
# 4. SAVE PROCESSED DATASET
# ==========================================

df.to_csv(
    "data/jobs_with_skills.csv",
    index=False
)


# ==========================================
# 5. COUNT SKILLS
# ==========================================

skill_counter = Counter()

for skills in df["extracted_skills"]:
    skill_counter.update(skills)


# ==========================================
# 6. DISPLAY TOP 20 SKILLS
# ==========================================

print("\n===== TOP 20 SKILLS =====")

for skill, count in skill_counter.most_common(20):
    print(f"{skill}: {count}")


# ==========================================
# 7. COMPLETION MESSAGE
# ==========================================

print("\nSkill extraction completed!")

print(
    "\nSaved processed dataset to: "
    "data/jobs_with_skills.csv"
)
