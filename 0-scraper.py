"""
MyCareersFuture Job Scraper

Runs a scrape of job listings based on search details specified below.

Saves results to a .json file.

-----------

CONFIGURE YOUR SEARCH

- Go to [mycareersfuture.gov.sg](mycareersfuture.gov.sg) and apply a search using the specs you want. (e.g. min salary, full time/contract/etc...)
- Open web developer tools and go to Network. Refresh the page. (These instructions for Firefox, but Chrome should be similar)
- Find the row item that says `GET`, `api.mycareersfuture.gov.sg` `search?search=data&salary=...` (this being whatever you specced)
- Right click, Copy Value, Copy URL parameters. Below was my example.
- You could also copy as curl command, send to chatGPT and ask it to convert it for you for as a Python request.

```
      search=data
      salary=6000
      positionLevel=Executive
      positionLevel=Junior%20Executive
      positionLevel=Fresh%2Fentry%20level
      sortBy=relevancy
      page=0
```

Set the data variable to the search you want, and run.

"""


import logging
import os

import requests
import yaml
from dotenv import load_dotenv

from src.mycareersfuture import MyCareersFutureListings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def read_yaml_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


file_path = "conf/base/config.yml"
config = read_yaml_config(file_path)
print(config)

# Load environment variables from .env
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# ###############!   CONFIGURE SEARCH   ################

# data = {
#     "sessionId": "",
#     "search": "data",
#     "salary": 6000,
#     "positionLevels": ["Executive", "Junior Executive", "Fresh/entry level"],
#     "postingCompany": [],
# }


#######################################################


##### RUN SEARCH AND SAVE TO FILE #####

mcf_listgs = MyCareersFutureListings(sleep_delay=config["scraper_delay"])
listings = mcf_listgs.scrape_listings(
    data=config["scraper_query"], start_url=config["scraper_starturl"]
)
listings = mcf_listgs.expand_listings()
mcf_listgs.save_json(json_save_file=config["scraper_results_file"])

# listings = mcf_listgs.load_json(json_load_file=JSON_SAVE_FILE)
