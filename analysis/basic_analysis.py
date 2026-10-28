import pandas as pd


# Load cleaned dataset
df = pd.read_csv("data/cleaned_postings.csv")


print("===== DATASET INFORMATION =====")
print("Number of jobs:", len(df))
print("Number of columns:", len(df.columns))


print("\n===== MISSING VALUES =====")
print(df.isnull().sum())


print("\n===== TOP JOB TITLES =====")
print(df["title"].value_counts().head(20))


print("\n===== TOP LOCATIONS =====")
print(df["location"].value_counts().head(20))


print("\n===== EXPERIENCE LEVELS =====")
print(df["formatted_experience_level"].value_counts())


print("\n===== WORK TYPES =====")
print(df["formatted_work_type"].value_counts())


print("\n===== REMOTE JOBS =====")
print(df["remote_allowed"].value_counts(dropna=False))