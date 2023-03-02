from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import urllib.request
import os

# Set up Selenium options
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# Navigate to homepage
driver.get('https://www.classcentral.com')
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find all links on the homepage
homepage_links = [a['href'] for a in soup.find_all('a', href=True)]

# Create a directory to store scraped content
if not os.path.exists('scraped_content'):
    os.mkdir('scraped_content')

# Download homepage HTML
homepage_html = driver.page_source
with open('scraped_content/homepage.html', 'w') as f:
    f.write(homepage_html)

# Download all CSS files referenced on homepage
for css_link in soup.find_all('link', {'rel': 'stylesheet'}):
    css_url = css_link['src']
    if css_url.startswith('//'):
        css_url = 'https:' + css_url
    elif css_url.startswith('/'):
        css_url = 'https:/' + css_url
    filename = os.path.join('scraped_content', os.path.basename(css_url))
    urllib.request.urlretrieve(css_url, filename)

# Download all JS files referenced on homepage
for js_link in soup.find_all('script', {'src': True}):
    js_url = js_link['src']
    if js_url.startswith('//'):
        js_url = 'https:' + js_url
    elif js_url.startswith('/'):
        js_url = 'https:/' + js_url
    filename = os.path.join('scraped_content', os.path.basename(js_url))
    urllib.request.urlretrieve(js_url, filename)

# Download all images referenced on homepage
for img in soup.find_all('img'):
    img_url = img['src']
    if img_url.startswith('//'):
        img_url = 'https:' + img_url
    elif img_url.startswith('/'):
        img_url = 'https:/' + img_url
    filename = os.path.join('scraped_content', os.path.basename(img_url))
    urllib.request.urlretrieve(img_url, filename)

# Download all single pages linked from homepage
for link in homepage_links:
    if link.startswith('http'):
        continue  # skip external links
    if link.startswith('/'):
        link = 'https://www.classcentral.com' + link  # fix relative links
    driver.get(link)
    page_soup = BeautifulSoup(driver.page_source, 'html.parser')
    page_html = driver.page_source
    with open('scraped_content/' + link.split('/')[-1], 'w') as f:
        f.write(page_html)
    # Download all CSS files referenced on the page
    for css_link in page_soup.find_all('link', {'rel': 'stylesheet'}):
        css_url = css_link['href']
        filename = os.path.join('scraped_content', os.path.basename(css_url))
        urllib.request.urlretrieve(css_url, filename)
    # Download all JS files referenced on the page
    for js_link in page_soup.find_all('script', {'src': True}):
        js_url = js_link['src']
        filename = os.path.join('scraped_content', os.path.basename(js_url))
        urllib.request.urlretrieve(js_url, filename)
    # Download all images referenced on the page
    for img in page_soup.find_all('img'):
        img_url = img['src']
        filename = os.path.join('scraped_content', os.path.basename(img_url))
        urllib.request.urlretrieve(img_url, filename)

# Close the Selenium driver
driver.quit()
