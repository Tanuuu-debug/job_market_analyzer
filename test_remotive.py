
import requests

url = "https://remotive.com/api/remote-jobs"

keywords = [
    "data analyst",
    "business analyst",
    "software engineer",
    "associate software engineer",
    "data scientist",
    "intern"
]

for keyword in keywords:
    print(f"\n{'=' * 55}")
    print(f"Searching: {keyword}")

    try:
        response = requests.get(
            url,
            params={"search": keyword, "limit": 100},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        jobs = data.get("jobs", [])

        # Only keep listings that explicitly mention India
        # or worldwide eligibility in the candidate location.
        india_jobs = [
            job for job in jobs
            if any(
                term in str(
                    job.get("candidate_required_location", "")
                ).lower()
                for term in ["india", "worldwide", "anywhere"]
            )
        ]

        print("Matching API results:", len(jobs))
        print("Potentially eligible for India:", len(india_jobs))

        for job in india_jobs[:5]:
            print("\nTitle:", job.get("title", "Unknown"))
            print("Company:", job.get("company_name", "Unknown"))
            print(
                "Eligible location:",
                job.get("candidate_required_location", "Not specified")
            )
            print("Job type:", job.get("job_type", "Not specified"))
            print("Apply:", job.get("url", "Not available"))

    except requests.RequestException as error:
        print("API request failed:", error)
    except ValueError:
        print("The API response was not valid JSON.")
