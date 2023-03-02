import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def download_resource(url, folder_path):
    try:
        if url.startswith('data:'):
            print(f"Skipping resource: {url}")
            return

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # Extract the filename from the URL
            filename = url.split('/')[-1]
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded resource: {url}")
        else:
            print(
                f"Failed to download resource: {url}, status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download resource: {url}, error: {e}")


def download_page(url, folder_path):
    """
    Downloads the specified page from the given URL and saves it to the specified folder.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    page_folder = os.path.join(folder_path, url.split('/')[-1])
    if not os.path.exists(page_folder):
        os.makedirs(page_folder)
    with open(os.path.join(page_folder, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(str(soup))
    resources = soup.find_all(
        ['link', 'script', 'img', 'video', 'audio', 'source', 'iframe'])
    for resource in resources:
        if resource.name in ['link', 'script', 'iframe']:
            url = resource.get('src') or resource.get('href')
        else:
            url = resource.get('src') or resource.get(
                'data-src') or resource.get('poster')
        if not url:
            continue
        if 'https://www.googletagmanager.com' in url:
            continue
        resource_url = requests.compat.urljoin(response.url, url)
        download_resource(resource_url, page_folder)


def download_website(url, folder_path):
    """
    Downloads the entire website from the given URL and saves it to the specified folder.
    """
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')

    # Set the path for the Chrome driver
    chromedriver_path = '/home/s13g/Documents/Downloads/chromedriver/chromedriver'

    # Initialize the Chrome browser driver
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
    driver.get(url)
    # Wait for the Cloudflare security check to complete
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # Scroll down to the end of the page to trigger the lazy-loading images to load
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for the lazy-loading images to fully load
    time.sleep(30)  # You can adjust the time based on the website's loading speed

    # Get the HTML content of the website
    html_content = driver.page_source
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    # driver.quit()
    links = [requests.compat.urljoin(url, link.get('href'))
             for link in soup.find_all('a') if link.get('href')]
    for link in links:
        print(link)
        download_page(link, folder_path)
        time.sleep(1)


download_website('https://www.classcentral.com',
                 '/home/s13g/Projects/Scraper/cc')
