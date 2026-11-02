# Job Hunter

A small Python job-monitoring agent that watches job listings and notifies me when a new job matching my interests appears.

## Why I built this

Finding a job isn't only about being a good candidate.

You can have the right skills, the right projects, and a CV that fits the position — but if you don't apply in time, you might not even get the chance to interview.

Junior and internship positions can receive a **large number of applications**, and job postings can disappear or become much more competitive surprisingly quickly. Being aware that a relevant position was posted can make a real difference.

That's what this project is trying to solve.

Instead of manually checking job websites over and over again, I wanted to build something that could do it for me:

> **Find relevant jobs → detect new ones → notify me as soon as possible.**

It's also a good excuse to combine several things I've been learning in Python, automation, databases, APIs, and eventually DevOps.

---

## What it does right now

The current version monitors the **DEV.BG Junior/Intern** job listings.

It:

* Scrapes job listings using `Requests` and `BeautifulSoup`
* Extracts:

  * Job title
  * Company
  * Link
  * Posting date
  * Technologies
* Checks the job against a list of keywords
* Stores matching jobs in SQLite
* Detects whether a job has already been seen
* Sends a Telegram notification when a **new matching job** is found
* Runs automatically using APScheduler

Current keywords:

```text
Python
Django
Docker
```

The goal is not to apply automatically or make decisions for me. It's simply meant to make sure I **don't miss relevant opportunities because I didn't see the posting in time.**

---

## How it works

```text
                DEV.BG
                   ↓
              Requests
                   ↓
           BeautifulSoup
                   ↓
            Extract jobs
                   ↓
          Keyword matching
                   ↓
               SQLite
                   ↓
          Is the job already
             in the database?
              ↙          ↘
            YES           NO
             ↓             ↓
          Ignore       New job
                           ↓
                    Telegram alert
```

---

## Technologies

* Python
* Requests
* BeautifulSoup
* SQLite
* Regular Expressions
* python-dotenv
* APScheduler
* Telegram Bot API

---

## What I've learned from building it

This project started as a simple web scraper, but it has already turned into something much more useful for learning.

I've worked with:

* HTTP requests
* HTML parsing
* Web scraping
* Dictionaries and lists
* Functions and code organization
* Regular expressions
* SQLite databases
* SQL `INSERT OR IGNORE`
* Environment variables
* Telegram API requests
* Scheduling Python programs
* Detecting new records
* Debugging API and database errors

One of the things I like about this project is that I'm building it piece by piece instead of trying to create the entire system at once.

---

## Current status

### Completed

* [x] DEV.BG scraper
* [x] Job information extraction
* [x] Keyword filtering
* [x] SQLite database
* [x] Duplicate/new job detection
* [x] Telegram bot
* [x] Telegram notifications
* [x] Automatic scheduled checks

### Next steps

* [ ] Improve error handling
* [ ] Improve Telegram notification formatting
* [ ] Clean up and refactor the code
* [ ] Add more keywords and better matching
* [ ] Monitor additional job websites
* [ ] Move from SQLite to PostgreSQL
* [ ] Dockerize the application
* [ ] Use Docker Compose
* [ ] Set up CI/CD
* [ ] Deploy the agent so it can run continuously
* [ ] Experiment with smarter job matching

---

## The bigger goal

The end goal is to turn this from a simple scraper into a small **job-hunting assistant**.

Eventually, I'd like it to understand more than just whether a job contains the word `Python`.

For example, it could consider:

* Technologies
* Job title
* Experience requirements
* Junior/intern level
* Location
* Remote/hybrid options
* Skills from my CV

But for now, I'm keeping it simple and building the fundamentals first.

---

## Note!

This project is intended as a learning and personal automation project. It is designed to check publicly available job listings and notify me about relevant opportunities. It does not automatically apply for jobs.
