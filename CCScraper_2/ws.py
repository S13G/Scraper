import os
import time
import requests
from urllib.parse import urlparse, urljoin, unquote
from bs4 import BeautifulSoup
import magic
from zenrows import ZenRowsClient


# Set the API URL and your API key
client = ZenRowsClient(
    "e2454792f5b06a34000e8b4dee3c698528f4b741")

url = "https://www.classcentral.com"

params = {"js_render": "true", "antibot": "true", "premium_proxy": "true",
          "proxy_country": "gb", "session_id": "5"}

# Add a User-Agent header to the requests sent by the ZenRowsClient
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

# Send the API request and get the response
response = client.get(url, params=params, headers=headers)

# Get the HTML content of the website from the API response
html_content = response.content
print(html_content)

# If the HTML content is a file, read its contents
if os.path.isfile(html_content):
    with open(html_content, 'r') as f:
        html_content = f.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Extract all the links from the homepage (index.html)
links = soup.find_all('a')

# Initialize the set of downloaded resources
resources = set()

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
    link_response = client.get(link_url, params=params, headers=headers)
    time.sleep(10)
    link_html_content = link_response.text
    print(link_html_content)

    # Parse the HTML using BeautifulSoup
    link_soup = BeautifulSoup(link_html_content, 'html.parser')

    # Download all the resources (images, CSS files, JS files) from the page
    for resource in link_soup.find_all(['img', 'link', 'script']):
        url = resource.get('src') or resource.get('href')
        if not url or 'ccweb.imgix.net' in url or "d3f1iyfxxz8i1e.cloudfront.net" in url or url.startswith('data:'):
            continue

        # Make sure the URL is absolute
        url = urljoin(link_url, url)

        # Download the resource and save it to the appropriate file
        response = requests.get(url, headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}, params=params)
        content_type = response.headers.get('content-type')

        if 'text' in content_type or 'html' in content_type:
            parsed_url = urlparse(url)
            path = parsed_url.path if parsed_url.path else 'index.html'
            filename = os.path.join(
                download_directory, unquote(os.path.basename(path)))
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
        else:
            parsed_url = urlparse(url)
            path = parsed_url.path if parsed_url.path else 'index.html'
            filename = os.path.join(
                download_directory, unquote(os.path.basename(path)))
            if os.path.isdir(filename):
                continue
            with open(filename, 'wb') as f:
                f.write(response.content)

    # Download the HTML file of the page and save it to the appropriate file
    parsed_url = urlparse(url)
    path = parsed_url.path if parsed_url.path else 'index.html'
    filename = os.path.join(
        download_directory, unquote(os.path.basename(path)))
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(link_html_content)

    # Print a summary of the downloaded resources
    print(f'Downloaded {filename}({len(resources)} resources')

    #     # Replace the URL in the HTML content with the local file path
    #     local_url = os.path.join(os.getcwd(), filepath)
    #     link_html_content = html_content.replace(url, local_url)
    #     resources.add(local_url)
    #     print(resources)

    # # Save the HTML content to a file in the download directory
    # filename = unquote(os.path.basename(urlparse(url).path))
    # if not filename:
    #     filename = 'index.html'
    # filepath = os.path.join(download_directory, filename)
    # with open(filepath, 'w') as f:
    #     f.write(link_html_content)
