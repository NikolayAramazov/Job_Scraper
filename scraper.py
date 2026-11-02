import requests
import re
from bs4 import BeautifulSoup
import sqlite3
import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from openai import OpenAI
import json, os, re, time

load_dotenv()

llm = OpenAI(base_url=os.getenv("LLM_BASE_URL"), api_key=os.getenv("LLM_API_KEY"))

SYSTEM = (
    "You write concise, honest cover letters for a junior/intern applicant. "
    "Only claim skills and experience that appear in the CV. Never invent anything. "
    "Keep the letter under 180 words, no clichés. "
    'Reply with JSON only: {"fit_score": 0-10, "reasons": "one sentence", "cover_letter": "..."}'
)


def draft_application(job, description=""):
    cv = open("cv.txt", encoding="utf-8").read()
    prompt = (
        f"CV:\n{cv}\n\n"
        f"Job: {job['title']} at {job['company']}\n"
        f"Technologies: {', '.join(job['technologies'])}\n"
        f"Description:\n{description or '(not available)'}"
    )

    for attempt in range(3):
        try:
            resp = llm.chat.completions.create(
                model=os.getenv("LLM_MODEL"),
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
            )
            text = resp.choices[0].message.content
            match = re.search(r"\{.*\}", text, re.DOTALL)
            return json.loads(match.group(0))
        except Exception as e:
            print(f"Draft attempt {attempt + 1} failed:", e)
            time.sleep(20 * (attempt + 1))  # backs off on 429s
    return None  # caller falls back to the plain alert

token = os.getenv("TELEGRAM_BOT_TOKEN")

url_bot = f"https://api.telegram.org/bot{token}/sendMessage"
chat_id = os.getenv("TELEGRAM_CHAT_ID")


url_dev = "https://dev.bg/company/jobs/junior-intern/"


keywords = [
    "python",
    "django",
    "docker",
]


def matches_keywords(job):
    search_text = job["title"] + " " + " ".join(job["technologies"])
    search_text = search_text.lower()

    for word in keywords:
        result = re.search(r"\b" + word + r"\b", search_text)

        if result:
            return True

    return False



HEADERS = {"User-Agent": "Mozilla/5.0 (personal job-alert script)"}

def scrape_dev_bg():
    response = requests.get(url_dev, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    all_jobs = []
    for el in soup.find_all("div", class_="job-list-item"):
        try:
            tech_wrap = el.find("div", class_="tech-stack-wrap")
            techs = [
                t.find("img")["title"]
                for t in (tech_wrap.find_all("div", class_="component-square-badge") if tech_wrap else [])
                if t.find("img")
            ]
            all_jobs.append({
                "title": el.find("h6", class_="job-title").get_text(strip=True),
                "link": el.find("a")["href"],
                "company": el.find("span", class_="company-name").get_text(strip=True),
                "date": el.find("span", class_="date").get_text(strip=True),
                "technologies": techs,
            })
        except (AttributeError, KeyError, TypeError) as e:
            print("Skipping malformed listing:", e)
    return all_jobs

def save_job(job):
    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            link TEXT UNIQUE,
            date TEXT
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO jobs (title, company, link, date)
        VALUES (?, ?, ?, ?)
    """, (
        job["title"],
        job["company"],
        job["link"],
        job["date"],
    ))

    is_new = cursor.rowcount == 1

    connection.commit()
    connection.close()

    return is_new

def send_telegram_message(job, draft=None):
    message = f"New job found!\n\n{job['title']}\nCompany: {job['company']}\n{job['link']}"
    if draft:
        message += (
            f"\n\nFit: {draft['fit_score']}/10 - {draft['reasons']}"
            f"\n\n--- Cover letter ---\n{draft['cover_letter']}"
        )
    r = requests.post(url_bot, data={"chat_id": chat_id, "text": message[:4000]})
    print("Telegram:", r.status_code)


def run_scraper():
    for job in scrape_dev_bg():
        if matches_keywords(job) and save_job(job):
            draft = draft_application(job)
            send_telegram_message(job, draft)
            time.sleep(5)  # stay under the per-minute limit


scheduler = BlockingScheduler()

scheduler.add_job(run_scraper, "interval", hours=1)
scheduler.start()
scheduler.start()

