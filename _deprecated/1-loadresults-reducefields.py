import logging
import os

import requests
from dotenv import load_dotenv

from src.mycareersfuture import MyCareersFutureListings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


JSON_LOAD_FILE = "./jobslist.json"
SLEEP_DELAY = 0.5

# Load environment variables from .env
load_dotenv()


mcf_listings = MyCareersFutureListings(sleep_delay=SLEEP_DELAY)
listings = mcf_listings.load_json(json_load_file=JSON_LOAD_FILE)

reduced = []
for listing in listings:
    reduced.append(
        {
            "url": listing["metadata"]["jobDetailsUrl"],
            "job_title": listing["title"],
            "job_desc": listing["job_desc"],
            "company": listing["postedCompany"]["name"],
            "salary_min": listing["salary"]["minimum"],
            "salary_max": listing["salary"]["maximum"],
            "skills": ", ".join([skill["skill"] for skill in listing["skills"]]),
        }
    )

reduced[:2]


for listing in reduced:
    print(listing["job_desc"])
    print("\n\n\n")
