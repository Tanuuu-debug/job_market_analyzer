
import os
import re
import time
import html
import requests
import pandas as pd

# Add company board tokens from their public Greenhouse career URLs.
# Example: boards.greenhouse.io/companyname -> token is "companyname"
BOARD_TOKENS = [
    "wpp",
    "capco",
    "precisionaq",
    "precisionmedicinegroup",
    "arcanaanalytics",
]

OUTPUT_FILE = "data/greenhouse_jobs.csv"


def clean_html(text):
    if not text:
        return ""

    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


all_jobs = []

for token in BOARD_TOKENS:
    print(f"Collecting Greenhouse jobs: {token}")

    url = (
        "https://boards-api.greenhouse.io/v1/boards/"
        f"{token}/jobs"
    )

    try:
        response = requests.get(
            url,
            params={"content": "true"},
            timeout=30
        )
        response.raise_for_status()

        jobs = response.json().get("jobs", [])
        print(f"  Retrieved {len(jobs)} jobs")

        for job in jobs:
            location = job.get("location") or {}
            departments = job.get("departments") or []

            all_jobs.append({
                "job_id": f"greenhouse_{job.get('id')}",
                "title": job.get("title"),
                "company_name": token,
                "location": location.get("name"),
                "description": clean_html(job.get("content", "")),
                "salary_min": None,
                "salary_max": None,
                "contract_type": None,
                "contract_time": None,
                "created": job.get("updated_at"),
                "job_url": job.get("absolute_url"),
                "search_keyword": ", ".join(
                    d.get("name", "") for d in departments
                ),
                "source": "Greenhouse"
            })

        time.sleep(0.5)

    except requests.RequestException as error:
        print(f"  Failed for {token}: {error}")

if not all_jobs:
    print(
        "No jobs collected. Add valid company board tokens "
        "to BOARD_TOKENS and run again."
    )
else:
    df = pd.DataFrame(all_jobs)
    df = df.drop_duplicates(subset=["job_id"])

    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\n========== GREENHOUSE SUMMARY ==========")
    print(f"Unique jobs: {len(df)}")
    print(f"Companies: {df['company_name'].nunique()}")
    print(f"Saved to: {OUTPUT_FILE}")
