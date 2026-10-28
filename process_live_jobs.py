import os
import re
import pandas as pd
from collections import Counter

from analysis.skills import SKILLS

# ---------------- CONFIGURATION ----------------

DATA_DIR = "data"

ADZUNA_FILE = os.path.join(DATA_DIR, "live_jobs.csv")
GREENHOUSE_FILE = os.path.join(DATA_DIR, "greenhouse_jobs.csv")
JSEARCH_FILE = os.path.join(DATA_DIR, "jsearch_jobs.csv")

OUTPUT_FILE = os.path.join(DATA_DIR, "live_jobs_processed.csv")


# ---------------- LOAD SOURCE DATA ----------------

def load_source(file_path, source_name):
    if not os.path.exists(file_path):
        print(f"Source file not found: {file_path}")
        return pd.DataFrame()

    df = pd.read_csv(file_path)

    if df.empty:
        print(f"No records found in: {file_path}")
        return pd.DataFrame()

    # Preserve the source assigned by the collector when available.
    if "source" not in df.columns:
        df["source"] = source_name
    else:
        df["source"] = df["source"].fillna(source_name)

    required_columns = [
        "job_id",
        "title",
        "company_name",
        "location",
        "description",
        "salary_min",
        "salary_max",
        "contract_type",
        "contract_time",
        "created",
        "job_url",
        "source",
        "remote_allowed",
        "formatted_experience_level",
        "formatted_work_type",
        "normalized_salary",
        "search_keyword",
        "job_publisher",
    ]

    for column in required_columns:
        if column not in df.columns:
            df[column] = pd.NA

    return df[required_columns].copy()


# ---------------- TEXT CLEANING ----------------

def clean_text(value):
    if pd.isna(value):
        return ""

    return str(value).strip()


# ---------------- SKILL EXTRACTION ----------------

# Match skills using whole-word boundaries to reduce false positives.
SKILL_PATTERNS = {
    skill: re.compile(
        r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"
    )
    for skill in SKILLS
}


def extract_skills(description):
    text = clean_text(description).lower()

    if not text:
        return []

    found_skills = []

    for skill, pattern in SKILL_PATTERNS.items():
        if pattern.search(text):
            found_skills.append(skill.lower())

    return sorted(set(found_skills))


# ---------------- LOAD ALL SOURCES ----------------

print("Loading job postings from all sources...")

adzuna_df = load_source(ADZUNA_FILE, "Adzuna")
greenhouse_df = load_source(GREENHOUSE_FILE, "Greenhouse")
jsearch_df = load_source(JSEARCH_FILE, "JSearch")

frames = [
    df
    for df in [adzuna_df, greenhouse_df, jsearch_df]
    if not df.empty
]

if not frames:
    raise ValueError(
        "No job data found. Run the Adzuna, Greenhouse, "
        "and JSearch collectors first."
    )

df = pd.concat(frames, ignore_index=True)

print(f"Rows before cleaning: {len(df)}")


# ---------------- NORMALIZE FIELDS ----------------

text_columns = [
    "job_id",
    "title",
    "company_name",
    "location",
    "description",
    "job_url",
    "source",
    "job_publisher",
]

for column in text_columns:
    df[column] = df[column].apply(clean_text)

# Normalize empty strings to missing values for identifiers.
for column in ["job_id", "job_url"]:
    df[column] = df[column].replace("", pd.NA)

# Normalize source labels.
df["source"] = df["source"].replace("", "Unknown")


# ---------------- REMOVE INVALID RECORDS ----------------

df = df[
    (df["title"] != "")
    & (
        (df["description"] != "")
        | df["job_url"].notna()
    )
].copy()

print(f"Rows after removing invalid records: {len(df)}")


# ---------------- DEDUPLICATION ----------------

# First remove duplicates using source-independent job IDs.
# IDs from different providers can collide, so include the source.
df["_job_id_key"] = (
    df["source"].str.lower()
    + "::"
    + df["job_id"].fillna("").astype(str)
)

has_id = df["job_id"].notna()

with_ids = df[has_id].drop_duplicates(
    subset=["_job_id_key"],
    keep="first"
)

without_ids = df[~has_id]

df = pd.concat(
    [with_ids, without_ids],
    ignore_index=True
)

df = df.drop(columns=["_job_id_key"])

# Deduplicate exact application URLs across sources.
df["_url_key"] = (
    df["job_url"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.rstrip("/")
    .str.lower()
)

has_url = df["_url_key"] != ""

with_urls = df[has_url].drop_duplicates(
    subset=["_url_key"],
    keep="first"
)

without_urls = df[~has_url]

df = pd.concat(
    [with_urls, without_urls],
    ignore_index=True
).drop(columns=["_url_key"])

print(f"Rows after deduplication: {len(df)}")


# ---------------- EXTRACT SKILLS ----------------

print("Extracting skills from job descriptions...")

df["extracted_skills"] = df["description"].apply(
    extract_skills
)


# ---------------- SAVE PROCESSED DATA ----------------

os.makedirs(DATA_DIR, exist_ok=True)

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ---------------- SUMMARY ----------------

print("\n========== MULTI-SOURCE SUMMARY ==========")

print(f"Total unique postings: {len(df):,}")

print(
    f"Unique companies: "
    f"{df.loc[df['company_name'] != '', 'company_name'].nunique():,}"
)

print(
    f"Unique job titles: "
    f"{df.loc[df['title'] != '', 'title'].nunique():,}"
)

print("\nPostings by source:")
print(df["source"].value_counts().to_string())

print("\nTop 15 skills across collected postings:")

skill_counts = Counter()

for skills in df["extracted_skills"]:
    if isinstance(skills, list):
        skill_counts.update(skills)

for skill, count in skill_counts.most_common(15):
    print(f"{skill}: {count}")

print(f"\nSaved processed data to: {OUTPUT_FILE}")