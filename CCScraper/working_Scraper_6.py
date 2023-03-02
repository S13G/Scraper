import os
import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# specify the path to the Chrome driver executable
chrome_driver_path = "/home/s13g/Documents/Downloads/chromedriver/chromedriver"
driver = webdriver.Chrome(service=Service(executable_path=chrome_driver_path))

# navigate to the website
url = 'https://www.classcentral.com'
driver.get(url)

# wait for the page to load completely
time.sleep(2)
wait = WebDriverWait(driver, 20)
# wait for all images to load
wait.until(EC.presence_of_element_located((By.XPATH, "//img")))
# create a BeautifulSoup object and find all links on the homepage
soup = BeautifulSoup(driver.page_source, 'html.parser')
homepage_links = soup.find_all('a')

# create a directory to store the scraped files
if not os.path.exists('files'):
    os.makedirs('files')

# scrape the homepage
homepage_file_path = 'files/homepage.html'
with open(homepage_file_path, 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

# loop through each link on the homepage and scrape the linked pages
for link in homepage_links:
    # get the URL and file path
    link_url = link.get('href')
    if not link_url:
        continue  # skip links without a URL
    file_path = 'files/' + link_url.replace('/', '_')
    if not file_path.endswith('.html'):
        file_path += '.html'

    # check if the file has already been scraped
    if os.path.exists(file_path):
        continue

    # navigate to the link and get the page source
    try:
        driver.get(link_url)
    except:
        continue  # skip invalid URLs
    page_source = driver.page_source

    # create a BeautifulSoup object and save the page source to a file
    soup = BeautifulSoup(page_source, 'html.parser')

    # update links on the page to point to the local versions of the pages
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href and not href.startswith('#'):
            local_href = href.replace(url, '')
            local_href = re.sub(r'^/$', '/index.html', local_href)
            local_href = re.sub(r'/$', '.html', local_href)
            link['href'] = local_href

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    # get all css, js, and image links and download the files
    css_links = soup.find_all('link', {'rel': 'stylesheet'})
    js_links = soup.find_all('script', {'src': True})
    img_links = soup.find_all('img', {'src': True})
    all_links = css_links + js_links + img_links
    for link in all_links:
        file_url = link.get('href') or link.get('src')
        if not file_url:
            continue
        if file_url.startswith('/'):
            file_url = url + file_url
        file_path = 'files/' + file_url.replace('/', '_')
        if len(file_path) > 255:
            file_path = 'files/' + str(hash(file_url)) + '.html'
        with open(file_path, 'wb') as f:
            f.write(requests.get(file_url).content)

# close the driver
driver.quit()
