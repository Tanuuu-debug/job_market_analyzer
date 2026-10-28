
import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

if not APP_ID or not APP_KEY:
    raise ValueError(
        "Adzuna credentials not found. Check your .env file."
    )

BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"

SEARCH_TERMS = [
    "data analyst",
    "business analyst",
    "software engineer",
    "associate software engineer",
    "data scientist",
    "data analyst intern",
    "software engineer intern",
]

def fetch_jobs(keyword, results_per_page=50):
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": keyword,
        "where": "India",
        "content-type": "application/json",
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30,
    )

    if not response.ok:
        print(
            f"Request failed for '{keyword}': "
            f"HTTP {response.status_code}"
        )
        print(response.text[:300])
        return []

    data = response.json()
    jobs = data.get("results", [])

    records = []

    for job in jobs:
        location = job.get("location") or {}
        company = job.get("company") or {}
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")

        records.append({
            "source": "Adzuna",
            "search_keyword": keyword,
            "job_id": job.get("id"),
            "title": job.get("title"),
            "company_name": company.get("display_name"),
            "location": location.get("display_name"),
            "description": job.get("description"),
            "job_url": job.get("redirect_url"),
            "created": job.get("created"),
            "salary_min": salary_min,
            "salary_max": salary_max,
            "contract_type": job.get("contract_type"),
            "contract_time": job.get("contract_time"),
            "category": (
                job.get("category") or {}
            ).get("label"),
        })

    return records


def main():
    all_jobs = []

    for keyword in SEARCH_TERMS:
        print(f"\nSearching India for: {keyword}")

        try:
            jobs = fetch_jobs(keyword)
            print(f"Jobs returned: {len(jobs)}")
            all_jobs.extend(jobs)

        except requests.RequestException as error:
            print(f"Network error for '{keyword}': {error}")

    if not all_jobs:
        print(
            "\nNo jobs collected. Check API access, credentials, "
            "and the API response before proceeding."
        )
        return

    df = pd.DataFrame(all_jobs)

    # Remove duplicate postings returned by multiple searches.
    if "job_id" in df.columns:
        df = df.drop_duplicates(
            subset=["job_id"],
            keep="first"
        )

    os.makedirs("data", exist_ok=True)

    output_path = "data/live_jobs.csv"
    df.to_csv(output_path, index=False)

    print("\n========== COLLECTION SUMMARY ==========")
    print("Unique postings collected:", len(df))
    print("Companies represented:", df["company_name"].nunique())
    print("Jobs by search term:")
    print(df["search_keyword"].value_counts().to_string())
    print("\nSaved to:", output_path)

    print("\nSample results:")
    print(
        df[["title", "company_name", "location", "job_url"]]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
