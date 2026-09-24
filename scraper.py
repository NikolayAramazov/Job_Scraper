import requests
from bs4 import BeautifulSoup

url = "https://dev.bg/company/jobs/junior-intern/"
response = requests.get(url)

all_jobs = []

keywords = [
    "python",
    "django",
    "docker",
]


def matches_keywords(job):
    search_text = job["title"] + " " + " ".join(job["technologies"])
    search_text = search_text.lower()

    for word in keywords:
        if word in search_text:
            return True

    return False


soup = BeautifulSoup(response.text, "html.parser")

jobs = soup.find_all("div", class_="job-list-item")


for job_element in jobs:
    job = {}
    technology_list = []

    title = job_element.find("h6", class_="job-title")
    job["title"] = title.get_text(strip=True)

    link = job_element.find("a")["href"]
    job["link"] = link

    company = job_element.find("span", class_="company-name")
    job["company"] = company.get_text(strip=True)

    date = job_element.find("span", class_="date")
    job["date"] = date.get_text(strip=True)

    technologies = job_element.find(
        "div",
        class_="tech-stack-wrap hide-for-small"
    )

    for tech in technologies.find_all(
        "div",
        class_="component-square-badge"
    ):
        image = tech.find("img")
        technology_list.append(image["title"])

    job["technologies"] = technology_list

    if matches_keywords(job):
        all_jobs.append(job)


print(len(all_jobs))

for job in all_jobs:
    print(job)