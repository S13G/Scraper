import os
import time
import requests
from urllib.parse import urlparse, urljoin, unquote
from bs4 import BeautifulSoup
import magic
from zenrows import ZenRowsClient

# Set the API URL and your API key
client = ZenRowsClient("5d1ca2812ca836b1e5cbd0d5e25e0cd7f3509efc")

url = "https://www.classcentral.com"

params = {"js_render": "true", "antibot": "false", "premium_proxy": "true",
          "proxy_country": "us", "original_status": "true", "device": "desktop", "session_id": "35301"}

# Send the API request and get the response
response = client.get(url, params=params)

# Get the HTML content of the website from the API response
html_content = response.text

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
    link_url = link.get('href')
    if not link_url:
        continue

    class_link = "https://www.classcentral.com"
    # Make sure the URL is absolute
    link_url = urljoin(class_link, link_url)
    print(f'processing link {link_url}')

    # Send another API request to get the HTML content of the link
    link_response = client.get(link_url, params=params)
    time.sleep(10)
    print(link_response)
    link_html_content = link_response.text
    print(link_html_content)

    # Parse the HTML using BeautifulSoup
    link_soup = BeautifulSoup(link_html_content, 'html.parser')
    resources = set()

    # Download all the resources (images, CSS files, JS files) from the page
    for resource in link_soup.find_all(['img', 'link', 'script']):
        url = resource.get('src') or resource.get('href')
        if not url or 'ccweb.imgix.net' in url or "d3f1iyfxxz8i1e.cloudfront.net" in url or url.startswith('data:'):
            continue

        # Make sure the URL is absolute
        url = urljoin(link_url, url)

        # Download the resource and save it to the download directory
        filename = unquote(os.path.basename(urlparse(url).path))
        if not filename:
            continue
        filepath = os.path.join(download_directory, filename.replace('/', '_'))
        if not os.path.exists(filepath):
            response = requests.get(url, stream=True)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)

        # Replace the URL in the HTML content with the local file path
        local_url = os.path.join(os.getcwd(), filepath)
        link_html_content = html_content.replace(url, local_url)
        resources.add(local_url)
        print(resources)

    # Save the HTML content to a file in the download directory
    filename = unquote(os.path.basename(urlparse(url).path))
    if not filename:
        filename = 'index.html'
    filepath = os.path.join(download_directory, filename)
    with open(filepath, 'w') as f:
        f.write(link_html_content)

    # Print a summary of the downloaded resources
    print(f'Downloaded {filename}({len(resources)} resources')
