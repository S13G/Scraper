# works but scrapes entire website

import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# set up the selenium webdriver
driver = webdriver.Chrome()

# set up the base url and directory paths
base_url = "https://www.classcentral.com"
base_dir = os.path.dirname(os.path.abspath(__file__))
files_dir = os.path.join(base_dir, "files")

# create the files directory if it doesn't exist
if not os.path.exists(files_dir):
    os.makedirs(files_dir)

# scrape the homepage
driver.get(base_url)
soup = BeautifulSoup(driver.page_source, "html.parser")

# find all links on the homepage
links = [link.get("href") for link in soup.find_all("a")]

# loop through each link and scrape the page
for link in links:
    try:
        # skip any links that don't start with the base_url
        if not link.startswith(base_url):
            continue

        # get the filename and directory path for the current link
        file_name = link.replace(base_url, "").lstrip("/")
        file_path = os.path.join(files_dir, file_name)

        # create any necessary subdirectories
        sub_dir = os.path.dirname(file_path)
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)

        # download and save the file
        if link.endswith(".css") or link.endswith(".js"):
            # for css and js files, use requests library
            with open(file_path, "wb") as f:
                f.write(requests.get(link).content)
        else:
            # for all other files, use selenium webdriver
            driver.get(link)
            with open(file_path, "wb") as f:
                f.write(driver.page_source.encode("utf-8"))

    except Exception as e:
        print(f"Error downloading {link}: {e}")

# quit the webdriver
driver.quit()
