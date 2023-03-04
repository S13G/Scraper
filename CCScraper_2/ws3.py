import os
import time
import requests
from urllib.parse import urlparse, urljoin, unquote
from bs4 import BeautifulSoup
import magic
from zenrows import ZenRowsClient

# Set the API URL and your API key
client = ZenRowsClient("12b3e3173b47cbbf9c1186d03bd80f7061a5c3b5")

url = "https://www.classcentral.com"

params = {"js_render": "true", "antibot": "true", "premium_proxy": "true",
          "proxy_country": "gb"}

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

# Initialize the set of downloaded resources
resources = set()

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
    link_html_content = link_response.text

    # Parse the HTML using BeautifulSoup
    link_soup = BeautifulSoup(link_html_content, 'html.parser')
    resource_content = link_html_content

    # Download all the resources (images, CSS files, JS files) from the page
    for resource in link_soup.find_all(['img', 'link', 'script']):
        url = resource.get('src') or resource.get('href')
        if not url or 'ccweb.imgix.net' in url or "d3f1iyfxxz8i1e.cloudfront.net" in url or url.startswith('data:'):
            continue

        # Make sure the URL is absolute
        url = urljoin(link_url, url)

        # Download the resource and save it to the download directory
        filename = os.path.basename(url)
        filepath = os.path.join(download_directory, filename)

        # Check if the resource has already been downloaded
        if url in resources:
            continue

        # Send a GET request to download the resource
        response = requests.get(url, allow_redirects=True)

        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to download {url}")
            continue

        # Get the MIME type of the resource
        mime_type = magic.from_buffer(response.content, mime=True)

        # Save the resource to the file system
        with open(filepath, 'wb') as f:
            f.write(response.content)

        print(f"Downloaded {url} ({mime_type})")

        # Add the downloaded resource to the set of downloaded resources
        resources.add(url)

print("All resources have been downloaded successfully!")
