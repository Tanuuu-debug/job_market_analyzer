import pandas as pd
import matplotlib.pyplot as plt

# Load cleaned dataset
df = pd.read_csv("data/cleaned_postings.csv")

print("Dataset loaded successfully!")
print("Number of jobs:", len(df))


# ==========================================
# 1. TOP JOB TITLES
# ==========================================

top_titles = df["title"].value_counts().head(15)

print("\n===== TOP 15 JOB TITLES =====")

for title, count in top_titles.items():
    print(f"{title}: {count}")


plt.figure(figsize=(10, 6))

plt.barh(top_titles.index[::-1], top_titles.values[::-1])

plt.xlabel("Number of Job Postings")
plt.ylabel("Job Title")
plt.title("Top 15 Job Titles")

plt.tight_layout()

plt.savefig("data/top_job_titles.png")

plt.show()


# ==========================================
# 2. EXPERIENCE LEVEL
# ==========================================

experience = df["formatted_experience_level"].value_counts()

print("\n===== EXPERIENCE LEVELS =====")

for level, count in experience.items():
    print(f"{level}: {count}")


plt.figure(figsize=(8, 5))

plt.bar(experience.index, experience.values)

plt.xlabel("Experience Level")
plt.ylabel("Number of Job Postings")
plt.title("Job Postings by Experience Level")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig("data/experience_levels.png")

plt.show()


# ==========================================
# 3. WORK TYPE
# ==========================================

work_type = df["formatted_work_type"].value_counts()

print("\n===== WORK TYPES =====")

for work, count in work_type.items():
    print(f"{work}: {count}")


plt.figure(figsize=(8, 5))

plt.bar(work_type.index, work_type.values)

plt.xlabel("Work Type")
plt.ylabel("Number of Job Postings")
plt.title("Job Postings by Work Type")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig("data/work_types.png")

plt.show()


# ==========================================
# 4. TOP LOCATIONS
# ==========================================

locations = df["location"].value_counts().head(15)

print("\n===== TOP 15 LOCATIONS =====")

for location, count in locations.items():
    print(f"{location}: {count}")


plt.figure(figsize=(10, 6))

plt.barh(locations.index[::-1], locations.values[::-1])

plt.xlabel("Number of Job Postings")
plt.ylabel("Location")
plt.title("Top 15 Job Locations")

plt.tight_layout()

plt.savefig("data/top_locations.png")

plt.show()


print("\n================================")
print("JOB MARKET ANALYSIS COMPLETED!")
print("================================")

print("\nCharts saved in the data folder.")