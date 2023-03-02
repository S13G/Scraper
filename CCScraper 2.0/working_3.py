# this code is getting the resources but not the html
import os
import time
import requests
from urllib.parse import urlparse, urljoin, unquote
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


# Set the options for the headless Chrome browser
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-running-insecure-content')

# Set the path for the Chrome driver
chromedriver_path = '/home/s13g/Documents/Downloads/chromedriver/chromedriver'

# Set the URL of the website you want to scrape
base_url = 'https://www.classcentral.com'

# Create a Service object with the path to the chromedriver executable
service = Service(executable_path=chromedriver_path)

# Initialize the Chrome browser driver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Load the website in the browser
driver.get(base_url)

# Wait for the Cloudflare security check to complete
WebDriverWait(driver, 12).until(
    EC.presence_of_element_located((By.TAG_NAME, 'body')))

# Scroll down to the end of the page to trigger the lazy-loading images to load
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# Wait for the lazy-loading images to fully load
time.sleep(15)  # You can adjust the time based on the website's loading speed

# Get the HTML content of the website
html_content = driver.page_source

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Create a directory to save the downloaded resources
download_directory = "/home/s13g/Projects/Scraper/resources"
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Find all the links on the homepage
homepage_links = soup.find_all('a')

# Download all the pages and resources linked from the homepage
for link in homepage_links:
    # Get the URL of the link
    url = link.get('href')
    if not url:
        continue
    if 'https://www.googletagmanager.com' in url:
        continue

    # Make sure the URL is absolute
    url = urljoin(base_url, url)

    # Load the page in the browser
    driver.get(url)

    # Wait for the Cloudflare security check to complete
    WebDriverWait(driver, 12).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # Scroll down to the end of the page to trigger the lazy-loading images to load
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for the lazy-loading images to fully load
    # You can adjust the time based on the website's loading speed
    time.sleep(15)

    # Get the HTML content of the page
    html_content = driver.page_source

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Download all the resources (HTML, CSS, JS, images, etc.)
    resources = soup.find_all(
        ['link', 'script', 'img', 'video', 'audio', 'source', 'iframe'])
    for resource in resources:
        # Get the URL of the resource
        url = resource.get('src') or resource.get('href')
        if not url:
            continue
        if 'https://www.googletagmanager.com' in url:
            continue

         # Make sure the URL is absolute
        url = urljoin(base_url, url)

        # Get the filename of the resource
        parsed_url = urlparse(unquote(url))
        filename = os.path.basename(parsed_url.path)
        if not filename:
            continue

        # # Simulate scrolling to the image element to trigger lazy loading
        # if resource.name == 'img':
        #     image_element = driver.find_element(
        #         By.XPATH, "//img[@src='" + url + "']")
        #     # # wait for image to be visible
        #     # wait = WebDriverWait(driver, 30)
        #     # image_element = wait.until(EC.visibility_of_element_located(
        #     #     (By.XPATH, "//img[@src='" + url + "']")))

        #     actions = ActionChains(driver)
        #     actions.move_to_element(image_element).perform()
        #     time.sleep(5)  # Wait for lazy loading
        #     driver.execute_script("window.scrollTo(0, 0);")  # Scroll back up

        # Download the resource
        response = requests.get(url)
        if resource.name == 'html':
            # Save the HTML content as index.html
            file_path = os.path.join(download_directory, 'index.html')
        else:
            file_path = os.path.join(download_directory, filename)
        with open(file_path, 'wb') as f:
            f.write(response.content)

driver.quit()
