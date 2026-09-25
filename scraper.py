import requests
import re
from bs4 import BeautifulSoup
import sqlite3
import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

load_dotenv()

#TELEGRAM_NOTIFICATION-------------------------------------

token = os.getenv("TELEGRAM_BOT_TOKEN")

url_bot = f"https://api.telegram.org/bot{token}/sendMessage"
chat_id = os.getenv("TELEGRAM_CHAT_ID")

data = {
    "chat_id": chat_id,
    "text": "Hello from my job scraper!"
}

#TELEGRAM_NOTIFICATION-------------------------------------

#WEBSITE_LINK---------------------------------------------

url = "https://dev.bg/company/jobs/junior-intern/"

#WEBSITE_LINK---------------------------------------------

keywords = [
    "python",
    "django",
    "docker",
]

#JOB_MATCHING---------------------------------------------

def matches_keywords(job):
    search_text = job["title"] + " " + " ".join(job["technologies"])
    search_text = search_text.lower()

    for word in keywords:
        result = re.search(r"\b" + word + r"\b", search_text)

        if result:
            return True

    return False

#JOB_MATCHING---------------------------------------------

#CREATING_DICT--------------------------------------------

def run_scraper():

    print("Running scraper...")

    all_jobs = []

    # SQL_DB---------------------------------------------------

    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS jobs
                   (
                       id      INTEGER PRIMARY KEY AUTOINCREMENT,
                       title   TEXT,
                       company TEXT,
                       link    TEXT UNIQUE,
                       date    TEXT
                   )
                   """)

    connection.commit()

    # SQL_DB---------------------------------------------------

    response = requests.get(url)

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

    #CREATING_DICT--------------------------------------------

        if matches_keywords(job):
            all_jobs.append(job)

    #DB_INSERT--------------------------------------------------

            cursor.execute(
                """
                INSERT OR IGNORE INTO jobs (title, company, link, date)
                VALUES (?, ?, ?, ?)
                """, (
                    job["title"],
                    job["company"],
                    job["link"],
                    job["date"],
                )
            )

            if cursor.rowcount == 1:
                print("NEW JOB:", job["title"])

    connection.commit()

#DB_INSERT--------------------------------------------------

scheduler = BlockingScheduler()

scheduler.add_job(run_scraper, "interval", seconds=5)

print("Job agent started. Checking every hour...")

scheduler.start()

