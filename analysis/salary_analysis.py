import pandas as pd
import matplotlib.pyplot as plt


# Load dataset
df = pd.read_csv("data/cleaned_postings.csv")

print("Dataset loaded successfully!")
print("Total job postings:", len(df))


# ==========================================
# 1. SALARY DATA AVAILABILITY
# ==========================================

salary_available = df["normalized_salary"].notna().sum()
salary_missing = df["normalized_salary"].isna().sum()

print("\n===== SALARY DATA =====")
print("Jobs with salary information:", salary_available)
print("Jobs without salary information:", salary_missing)


# ==========================================
# 2. BASIC SALARY STATISTICS
# ==========================================

salary_stats = df["norma lized_salary"].describe()

print("\n===== SALARY STATISTICS =====")
print(salary_stats)


# ==========================================
# 3. TOP JOB TITLES BY MEDIAN SALARY
# ==========================================

salary_by_title = (
    df.dropna(subset=["normalized_salary"])
    .groupby("title")["normalized_salary"]
    .agg(["count", "median"])
)

# Only consider titles with at least 20 postings
salary_by_title = salary_by_title[
    salary_by_title["count"] >= 20
]

salary_by_title = salary_by_title.sort_values(
    "median",
    ascending=False
).head(15)


print("\n===== TOP JOB TITLES BY MEDIAN SALARY =====")

for title, row in salary_by_title.iterrows():
    print(
        f"{title}: "
        f"${row['median']:,.0f} "
        f"({int(row['count'])} postings)"
    )


# ==========================================
# 4. SALARY CHART
# ==========================================

plt.figure(figsize=(10, 6))

plt.barh(
    salary_by_title.index[::-1],
    salary_by_title["median"][::-1]
)

plt.xlabel("Median Normalized Salary")
plt.ylabel("Job Title")
plt.title("Job Titles by Median Salary")

plt.tight_layout()

plt.savefig("data/salary_by_job_title.png")

plt.show()


print("\nSalary analysis completed!")
print("Chart saved to: data/salary_by_job_title.png")