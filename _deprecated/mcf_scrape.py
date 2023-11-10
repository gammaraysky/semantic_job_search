# import requests
# from bs4 import BeautifulSoup

# # URL of the job listing webpage
# url = "https://www.mycareersfuture.gov.sg/search?search=data&salary=6000&positionLevel=Executive&positionLevel=Junior%20Executive&positionLevel=Fresh%2Fentry%20level&sortBy=relevancy&page=0"

# # Send an HTTP GET request to the webpage
# response = requests.get(url)

# # Parse the HTML content of the page
# soup = BeautifulSoup(response.text, "lxml")

# # Find all div elements whose id contains "job-card"
# job_card_elements = soup.find_all("div", id=lambda x: x and "job-card" in x)

# # Initialize a dictionary to store the job listings
# job_listings = {}

# # Iterate through each job card element
# for index, job_card in enumerate(job_card_elements):
#     # Find the <a> href link and grab the href
#     link_element = job_card.find("a")
#     link = link_element["href"] if link_element else "Not found"

#     # Find the <p> element with data-cy="company-hire-info__company" and grab its content
#     company_element = job_card.find("p", {"data-cy": "company-hire-info__company"})
#     company = company_element.text if company_element else "Not found"

#     # Find the <span> element with data-cy="job-card__job-title" and grab its content
#     job_title_element = job_card.find("span", {"data-cy": "job-card__job-title"})
#     job_title = job_title_element.text if job_title_element else "Not found"

#     # Save the values in a dictionary
#     job_listings[index] = {"Link": link, "Company": company, "Job Title": job_title}

# # Print the job listings dictionary
# for index, job in job_listings.items():
#     print(f"Listing {index}:")
#     print(f"Link: {job['Link']}")
#     print(f"Company: {job['Company']}")
#     print(f"Job Title: {job['Job Title']}")
#     print()


# # from selenium import webdriver

# # # Initialize a Selenium WebDriver
# # driver = webdriver.Chrome(executable_path="/path/to/chromedriver")

# # # URL of the job listing webpage


# # url = "https://example.com/job-listings"

# # # Navigate to the webpage
# # driver.get(url)

# # # Find all div elements whose id contains "job-card"
# # job_card_elements = driver.find_elements_by_xpath('//div[contains(@id, "job-card")]')

# # # Initialize a dictionary to store the job listings
# # job_listings = {}

# # # Iterate through each job card element
# # for index, job_card in enumerate(job_card_elements):
# #     # Find the <a> href link and grab the href
# #     link_element = job_card.find_element_by_tag_name("a")
# #     link = link_element.get_attribute("href")

# #     # Find the <p> element with data-cy="company-hire-info__company" and grab its content
# #     company_element = job_card.find_element_by_css_selector(
# #         'p[data-cy="company-hire-info__company"]'
# #     )
# #     company = company_element.text

# #     # Find the <span> element with data-cy="job-card__job-title" and grab its content
# #     job_title_element = job_card.find_element_by_css_selector(
# #         'span[data-cy="job-card__job-title"]'
# #     )
# #     job_title = job_title_element.text

# #     # Save the values in a dictionary
# #     job_listings[index] = {"Link": link, "Company": company, "Job Title": job_title}

# # # Close the browser
# # driver.quit()

# # # Print the job listings dictionary
# # for index, job in job_listings.items():
# #     print(f"Listing {index}:")
# #     print(f"Link: {job['Link']}")
# #     print(f"Company: {job['Company']}")
# #     print(f"Job Title: {job['Job Title']}")
# #     print()
