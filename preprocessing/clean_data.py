import pandas as pd


# Load dataset
file_path = "data/postings.csv"

df = pd.read_csv(file_path)

print("Original dataset shape:", df.shape)


# Select useful columns
columns_needed = [
    "job_id",
    "company_name",
    "title",
    "description",
    "min_salary",
    "max_salary",
    "med_salary",
    "normalized_salary",
    "currency",
    "location",
    "formatted_work_type",
    "formatted_experience_level",
    "remote_allowed",
    "skills_desc",
    "views",
    "applies"
]

df = df[columns_needed]


# Remove duplicate job postings
df = df.drop_duplicates(subset="job_id")


# Remove rows without a job title
df = df.dropna(subset=["title"])


# Fill missing text values
text_columns = [
    "company_name",
    "description",
    "location",
    "formatted_work_type",
    "formatted_experience_level",
    "skills_desc"
]

for column in text_columns:
    df[column] = df[column].fillna("Unknown")


# Clean job titles
df["title"] = df["title"].str.strip()


# Clean company names
df["company_name"] = df["company_name"].str.strip()


# Save cleaned dataset
output_file = "data/cleaned_postings.csv"

df.to_csv(output_file, index=False)


print("Cleaning completed!")
print("Cleaned dataset shape:", df.shape)
print("Saved to:", output_file)