import os

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set up options to run Chrome in headless mode and disable image loading
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
prefs = {'profile.managed_default_content_settings.images': 2}
chrome_options.add_experimental_option('prefs', prefs)

# Start Chrome and navigate to the homepage
driver = webdriver.Chrome()
driver.get('https://www.classcentral.com')

# Extract all links from the homepage
soup = BeautifulSoup(driver.page_source, 'html.parser')
links = [link.get('href') for link in soup.find_all('a') if link.get('href')]

# Create a directory to store the scraped files
if not os.path.exists('files'):
    os.makedirs('files')

# Loop through the links and scrape each page
for link in links:
    try:
        # Skip links that don't start with http or https
        if not link.startswith('http'):
            continue

        # Navigate to the link and get the page source
        driver.get(link)
        page_source = driver.page_source

        # Save the HTML to a file
        file_path = os.path.join('files', link[link.index('//') + 2:].replace('/', '_') + '.html')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(page_source)

        # Extract and save all linked resources (CSS, JS, images)
        soup = BeautifulSoup(page_source, 'html.parser')
        for tag in soup.find_all(['link', 'script', 'img']):
            # Get the URL of the resource
            if tag.name == 'link':
                file_url = tag.get('href')
            else:
                file_url = tag.get('src')

            # Skip tags that don't have a URL
            if not file_url:
                continue

            # Skip external URLs (i.e. those that don't start with http or https)
            if not file_url.startswith('http'):
                continue

            # Download the resource and save it to a file
            file_path = os.path.join('files', file_url[file_url.index('//') + 2:].replace('/', '_'))
            with open(file_path, 'wb') as f:
                f.write(requests.get(file_url).content)

    except Exception as e:
        print(f"Error while scraping {link}: {e}")

# Quit Chrome
driver.quit()
