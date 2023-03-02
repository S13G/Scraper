import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

# set up selenium driver
driver = webdriver.Chrome()
driver.get("https://www.classcentral.com/")  # replace with your target website

# create directory to store files
dir_name = 'scraped_data'
if not os.path.exists(dir_name):
    os.makedirs(dir_name)

# get html content and write to file
html_content = driver.page_source
with open(os.path.join(dir_name, 'homepage.html'), 'w', encoding='utf-8') as f:
    f.write(html_content)

# get css and js links and download them
css_links = [link.get_attribute("href") for link in driver.find_elements(By.XPATH, "//link[@rel='stylesheet']")]
js_links = [link.get_attribute("src") for link in driver.find_elements(By.XPATH, "//script")]
for link in css_links + js_links:
    if link:
        driver.get(link)
        time.sleep(4)  # wait for the file to load completely
        content = driver.page_source
        filename = link.split('/')[-1]
        with open(os.path.join(dir_name, filename), 'w', encoding='utf-8') as f:
            f.write(content)

# scrape one level deep
links = [link.get_attribute("href") for link in driver.find_elements(By.XPATH, "//a")]
for link in links:
    if link and link.startswith("https://www.classcentral.com/"):  # replace with your target website
        driver.get(link)
        time.sleep(4)  # wait for the page to load completely
        # get html content and write to file
        html_content = driver.page_source
        filename = link.replace("https://www.classcentral.com/", "").replace("/", "_").strip("_") + '.html'
        with open(os.path.join(dir_name, filename), 'w', encoding='utf-8') as f:
            f.write(html_content)

# close selenium driver
driver.quit()

# link files together
for root, dirs, files in os.walk(dir_name):
    for file in files:
        if file.endswith('.html'):
            with open(os.path.join(root, file), 'r+', encoding='utf-8') as f:
                content = f.read()
                for filename in files:
                    if filename.endswith('.css') or filename.endswith('.js'):
                        file_path = os.path.join(root, filename)
                        if os.path.isfile(file_path):
                            with open(file_path, 'r', encoding='utf-8') as css_js_file:
                                css_js_content = css_js_file.read()
                                content = content.replace(filename, css_js_content)
                f.seek(0)
                f.write(content)
                f.truncate()
