import requests
from bs4 import BeautifulSoup

URL = "https://remoteok.com/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers)

print("Status code:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

jobs = soup.find_all("tr", class_="job")

print("Number of job rows:", len(jobs))

if jobs:
    print("\nFirst job HTML:\n")
    print(jobs[0].prettify()[:5000])
else:
    print("No job rows found.")