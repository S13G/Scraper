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

# Set the options for the headless Chrome browser
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-running-insecure-content')

# Set the path for the Chrome driver
chromedriver_path = '/home/s13g/Downloads/chromedriver/chromedriver'

# Set the URL of the website you want to scrape
url = 'https://www.classcentral.com/'

# Create a Service object with the path to the chromedriver executable
service = Service(executable_path=chromedriver_path)

# Initialize the Chrome browser driver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Load the website in the browser
driver.get(url)

# Wait for the Cloudflare security check to complete
WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.TAG_NAME, 'body')))

# Scroll down to the end of the page to trigger the lazy-loading images to load
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# Wait for the lazy-loading images to fully load
# time.sleep(10)  # You can adjust the time based on the website's loading speed

# Get the HTML content of the website
html_content = driver.page_source

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Extract all the links from the homepage (index.html)
links = soup.find_all('a')

# Create a directory to save the downloaded resources
download_directory = 'downloaded_resources'
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Iterate through each link and scrape their first page and resources
for link in links:
    # Get the URL of the link
    url = link.get('href')
    if not url:
        continue

    # Make sure the URL is absolute
    url = urljoin(driver.current_url, url)

    # Load the link in the browser and wait for it to load completely
    driver.get(url)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # Get the HTML content
    html_content = driver.page_source

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    resources = set()

    # Download all the resources (images, CSS files, JS files) from the page
    for resource in soup.find_all(['img', 'link', 'script']):
        url = resource.get('src') or resource.get('href')
        if not url or 'ccweb.imgix.net' in url or "d3f1iyfxxz8i1e.cloudfront.net" in url or url.startswith('data:'):
            continue

        # Make sure the URL is absolute
        url = urljoin(driver.current_url, url)

        # Download the resource and save it to the download directory
        filename = unquote(os.path.basename(urlparse(url).path))
        filepath = os.path.join(download_directory, filename.replace('/', '_'))
        if not os.path.exists(filepath):
            response = requests.get(url, stream=True)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)

        # Replace the URL in the HTML content with the local file path
        local_url = os.path.join(os.getcwd(), filepath)
        html_content = html_content.replace(url, local_url)
        resources.add(local_url)

    # Save the HTML content to a file in the download directory
    filename = unquote(os.path.basename(urlparse(url).path))
    if not filename:
        filename = 'index.html'
    filepath = os.path.join(download_directory, filename)
    with open(filepath, 'w') as f:
        f.write(html_content)

    # Print a summary of the downloaded resources
    print(f'Downloaded {filename} ({len(resources)} resources):')
    for resource in resources:
        print(f'  {resource}')


driver.quit()
