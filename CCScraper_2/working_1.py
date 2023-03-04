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
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.TAG_NAME, 'body')))

# Scroll down to the end of the page to trigger the lazy-loading images to load
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# Wait for the lazy-loading images to fully load
time.sleep(60)  # You can adjust the time based on the website's loading speed

# Get the HTML content of the website
html_content = driver.page_source

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Create a directory to save the downloaded resources
download_directory = 'downloaded_resources'
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Download all the resources (HTML, CSS, JS, images, etc.)
resources = soup.find_all(
    ['link', 'script', 'img', 'video', 'audio', 'source', 'iframe'])
for resource in resources:
    # Get the URL of the resource
    if resource.name in ['link', 'script', 'iframe']:
        url = resource.get('src') or resource.get('href')
    else:
        url = resource.get('src') or resource.get(
            'data-src') or resource.get('poster')
    if not url:
        continue

    # Make sure the URL is absolute
    url = urljoin(driver.current_url, url)

    # Download the resource
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # Get the filename of the resource
            parsed_url = urlparse(unquote(url))
            filename = os.path.basename(parsed_url.path)
            if not filename:
                filename = 'index.html'
            filepath = os.path.join(download_directory, filename)

            # Save the resource to the file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
    except Exception as e:
        print(f'Error downloading resource: {url}: {e}')

# Replace all the resource URLs in the HTML content with the local file paths
for resource in resources:
    # Get the URL of the resource
    if resource.name in ['link', 'script', 'iframe']:
        url = resource.get('src') or resource.get('href')
    else:
        url = resource.get('src') or resource.get(
            'data-src') or resource.get('poster')
    if not url:
        continue

    # Make sure the URL is absolute
    url = urljoin(driver.current_url, url)

    # Get the local file path of the resource
    parsed_url = urlparse(unquote(url))
    filename = os.path.basename(parsed_url.path)
    if not filename:
        filename = 'index.html'
    filepath = os.path.join(download_directory, filename)

    # Replace the resource URL with the local file path in the HTML content
    if resource.name in ['link', 'script', 'iframe']:
        resource['src'] = filepath
    else:
        resource['src'] = filepath if resource.get('src') else None
        resource['data-src'] = filepath if resource.get('data-src') else None
        resource['poster'] = filepath if resource.get('poster') else None
        with open(os.path.join(download_directory, 'index.html'), 'w') as f:
            f.write(str(soup))

driver.quit()
