import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")
API_URL = "https://jsearch.p.rapidapi.com/search-v2"

OUTPUT_FILE = "data/jsearch_jobs.csv"

SEARCH_QUERIES = [
    "Data Analyst jobs in India",
    "Business Intelligence Analyst jobs in India",
    "Data Scientist jobs in India",
]


def fetch_jobs(query):
    if not API_KEY:
        raise ValueError(
            "RAPIDAPI_KEY not found. Check your .env file."
        )

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }

    params = {
        "query": query,
        "page": "1",
        "num_pages": "1",
        "country": "in",
        "date_posted": "month",
    }

    response = requests.get(
        API_URL,
        headers=headers,
        params=params,
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"JSearch API error {response.status_code}: "
            f"{response.text[:500]}"
        )

    payload = response.json()

    if payload.get("status") == "ERROR":
        raise RuntimeError(
            f"JSearch error: "
            f"{payload.get('message', payload.get('error', 'Unknown error'))}"
        )

    jobs = payload.get("data", [])

    if isinstance(jobs, dict):
        jobs = jobs.get("jobs", [])

    if not isinstance(jobs, list):
        raise RuntimeError("Unexpected JSearch response format.")

    return jobs


def main():
    print("Collecting jobs from JSearch...")

    all_jobs = []

    for index, query in enumerate(SEARCH_QUERIES):
        print(f"\nSearching: {query}")

        try:
            jobs = fetch_jobs(query)
            print(f"Retrieved: {len(jobs)} jobs")
            all_jobs.extend(jobs)

        except (
            requests.RequestException,
            RuntimeError,
            ValueError,
        ) as exc:
            print(f"Search failed: {exc}")

        if index < len(SEARCH_QUERIES) - 1:
            time.sleep(1)

    if not all_jobs:
        print(
            "\nNo jobs collected. Check your API key, "
            "subscription, quota, endpoint, and internet connection."
        )
        return

    df = pd.DataFrame(all_jobs)

    def get_column(name):
        if name in df.columns:
            return df[name]
        return pd.Series(index=df.index, dtype="object")

    output = pd.DataFrame({
        "job_id": get_column("job_id"),
        "title": get_column("job_title"),
        "company_name": get_column("employer_name"),
        "location": get_column("job_location"),
        "description": get_column("job_description"),
        "salary_min": get_column("job_min_salary"),
        "salary_max": get_column("job_max_salary"),
        "created": get_column("job_posted_at_datetime_utc"),
        "job_url": get_column("job_apply_link"),
        "contract_type": get_column("job_employment_type"),
        "source": "JSearch",
        "search_keyword": "JSearch API",
    })

    optional_columns = {
        "remote_allowed": "job_is_remote",
        "job_country": "job_country",
        "job_publisher": "job_publisher",
        "job_city": "job_city",
        "job_state": "job_state",
        "salary_currency": "job_salary_currency",
        "salary_period": "job_salary_period",
    }

    for output_column, api_column in optional_columns.items():
        if api_column in df.columns:
            output[output_column] = df[api_column]

    # Remove postings without a title or application link.
    output["title"] = output["title"].replace(r"^\s*$", pd.NA, regex=True)
    output["job_url"] = output["job_url"].replace(r"^\s*$", pd.NA, regex=True)

    output = output.dropna(subset=["title", "job_url"])

    # Deduplicate by job ID and application URL.
    output["job_id"] = output["job_id"].replace(r"^\s*$", pd.NA, regex=True)

    output = output.drop_duplicates(
        subset=["job_id"],
        keep="first",
    )

    output = output.drop_duplicates(
        subset=["job_url"],
        keep="first",
    )

    if output.empty:
        print("No usable postings with titles and application links were found.")
        return

    os.makedirs("data", exist_ok=True)

    output.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n========== JSEARCH SUMMARY ==========")
    print(f"Unique postings: {len(output):,}")
    print(f"Companies: {output['company_name'].nunique():,}")
    print(f"Unique job titles: {output['title'].nunique():,}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nTop 10 job titles:")
    print(output["title"].value_counts().head(10).to_string())


if __name__ == "__main__":
    main()