import requests
import json
import time
import random
import re
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def strip_html_tags(text):
    """Remove HTML tags from a string using regular expressions."""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


class MyCareersFutureListings:
    def __init__(self, sleep_delay: float = 0.5) -> None:
        """
        Initialize the MyCareersFutureListings class.

        Args:
            sleep_delay (float): Sleep delay in seconds (default: 0.5).
        """

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.mycareersfuture.gov.sg/",
            "Content-Type": "application/json",
            "mcf-client": "jobseeker",
            "Origin": "https://www.mycareersfuture.gov.sg",
            "DNT": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Sec-GPC": "1",
            "If-None-Match": 'W/"1f5e-zqQckgiUZusumGRwub5JefH3dLA"',
            "TE": "trailers",
        }

        self.resp_jsons = []
        self.last_resp_json = None
        self.listings = []
        self.SLEEP_DELAY = sleep_delay

    def scrape_listings(self, data: dict, start_url: str) -> None:
        """
        Scrape job listings from the specified URL.

        Args:
            data (dict): JSON data for the request.
            start_url (str): The URL to start scraping from.

        Returns:
            None
        """

        ### loop to get all page splits
        while True:
            # on first attempt, last_resp_json doesn't exist, call request to `url`
            if self.last_resp_json is None:
                response = requests.post(start_url, headers=self.headers, json=data)
                self.last_resp_json = json.loads(response.text)
                self.resp_jsons.append(self.last_resp_json)
                break  # ! FIXME - added break so we only grab first page of results
            # on subsequent attempts, check if we reached last page
            if "next" not in self.last_resp_json["_links"].keys():
                break
            else:
                time.sleep(random.uniform(0, self.SLEEP_DELAY))
                response = requests.post(
                    self.last_resp_json["_links"]["next"]["href"],
                    headers=self.headers,
                    json=data,
                )
                self.last_resp_json = json.loads(response.text)
                self.resp_jsons.append(self.last_resp_json)

        return self.format_listings()

    def format_listings(self) -> dict:
        """
        Reformat the listings for cleaner presentation.

        Returns:
            dict: Formatted job listings.
        """
        self.listings = []
        for i in range(len(self.resp_jsons)):
            for j in range(len(self.resp_jsons[i]["results"])):
                self.listings.append(self.resp_jsons[i]["results"][j])

        return self.listings

    def save_json(self, json_save_file: str) -> None:
        """
        Save job listings to a JSON file.

        Args:
            json_save_file (str): File path to save the JSON data.

        Returns:
            None
        """
        with open(json_save_file, "w") as json_file:
            json_file.write(json.dumps(self.listings, indent=4))

    def load_json(self, json_load_file: str) -> dict:
        """
        Load job listings from a JSON file.

        Args:
            json_load_file (str): File path to load the JSON data.

        Returns:
            dict: Loaded job listings.
        """
        with open(json_load_file, "r") as json_file:
            self.listings = json.load(json_file)

        return self.listings

    def get_indiv_job_desc(self, job_uuid: str) -> dict:
        """
        Get the individual job description using the job UUID.

        Args:
            job_uuid (str): UUID of the job.

        Returns:
            dict: Job description details.
        """
        url_pattern = (
            "https://api.mycareersfuture.gov.sg/v2/jobs/"
            + job_uuid
            + "?updateApplicationCount=true"
        )

        response = requests.get(url_pattern, headers=self.headers)
        # print(response.text)

        json_response = json.loads(response.text)

        description = json_response["description"]
        description = strip_html_tags(description)

        description += "\n Required Skills: "
        for item in json_response["skills"]:
            description += ", "
            description += item["skill"]

        return description

    def expand_listings(self) -> dict:
        """
        Open each job listing and adds job description details to the
        listings.

        Returns:
            dict: Job listings with job descriptions.
        """

        # Regular expression pattern to match a UUID at the end of the URL
        pattern = r"[-\w]{32}$"

        for i, listing in enumerate(self.listings):
            # Use re.search to find the UUID
            match = re.search(pattern, listing["metadata"]["jobDetailsUrl"])

            if match:
                job_uuid = match.group()
                # logger.info("UUID: %s", job_uuid)
                time.sleep(random.uniform(0, self.SLEEP_DELAY))
                self.listings[i]["job_desc"] = self.get_indiv_job_desc(job_uuid)
            else:
                logger.info(
                    "UUID not found for %s", listing["metadata"]["jobDetailsUrl"]
                )

        return self.listings
