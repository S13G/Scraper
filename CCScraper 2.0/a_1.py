import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set the options for the web driver
# options = Options()
# options.headless = True
# options.add_argument('--disable-gpu')
# options.add_argument('--disable-extensions')

# Set the path to the web driver
driver_path = '/home/s13g/Documents/Downloads/chromedriver/chromedriver'

# Set the URL of the website you want to scrape
url = 'https://www.classcentral.com'

# Create a new instance of the web driver
driver = webdriver.Chrome(executable_path=driver_path)

# Load the homepage
driver.get(url)

# Get the page source and parse it with BeautifulSoup
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Create a folder to store the downloaded pages
if not os.path.exists('pages'):
    os.makedirs('pages')

# Save the homepage
filename = 'homepage.html'
with open('pages/' + filename, 'w') as f:
    f.write(str(soup))

# Find all links on the homepage
links = []
for link in soup.find_all('a'):
    link_url = link.get('href')
    if link_url.startswith(url):
        links.append(link_url)

# Visit each linked page and save it
for link in links:
    driver.get(link)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    filename = link.replace(url, '').replace('/', '') + '.html'
    with open('pages/' + filename, 'w') as f:
        f.write(str(soup))

# Close the web driver
driver.quit()
