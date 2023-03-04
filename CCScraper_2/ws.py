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

params = {"js_render": "true", "antibot": "false", "premium_proxy": "true",
          "proxy_country": "gb", "session_id": "5"}

# Add a User-Agent header to the requests sent by the ZenRowsClient
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

# Send the API request and get the response
response = client.get(url, params=params, headers=headers)

# Get the HTML content of the website from the API response
html_content = response.content

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

        # Check if the resource has already been downloaded
        filename = unquote(os.path.basename(urlparse(url).path))
        if filename in resources:
            continue

        # Make sure the URL is absolute
        url = urljoin(link_url, url)

        # Download the resource and save it to the appropriate file
        response = requests.get(url, headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}, params=params)
        content_type = response.headers.get('content-type')

        if not content_type:
            continue

        # Get the file extension from the content type
        file_extension = magic.from_buffer(
            response.content, mime=True).split('/')[1]
        file_extension = file_extension.split(';')[0]

        # Generate a unique filename for the resource based on its URL and file extension
        # parsed_url = urlparse(url)
        # filename = unquote(os.path.basename(parsed_url.path))
        # if not filename:
        #     filename = 'index'
        filename = f"{filename[:100]}.{file_extension}"
        i = 1
        while filename in resources:
            filename = f"{filename[:100]}_{i}.{file_extension}"
            i += 1

        # Save the resource to the appropriate file
        with open(os.path.join(download_directory, filename), 'wb') as f:
            f.write(response.content)

        # Add the downloaded resource to the set of downloaded resources
        resources.add(filename)

        # Replace the URL in the HTML content with the local file path
        local_path = os.path.join('.', download_directory, filename)
        existing_link = soup.find(
            link.name, attrs={'href': link.get('href'), 'src': link.get('src')})
        if existing_link:
            existing_link.replace_with(link_soup.new_tag(
                link.name, href=local_path) if link.name == 'a' else link_soup.new_tag(link.name, src=local_path))
        else:
            print('Could not find link to replace:', link)


# Save the modified HTML content to a file in the download directory
with open(os.path.join(download_directory, f"{filename}.html"), 'w') as f:
    f.write(str(link_soup))

print("Scraping complete!")
