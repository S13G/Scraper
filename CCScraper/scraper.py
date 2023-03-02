import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# create directory to store files
dir_name = 'scraped_data'
if not os.path.exists(dir_name):
    os.makedirs(dir_name)

# initialize Selenium driver
driver = webdriver.Chrome()

# scrape homepage
driver.get("https://www.classcentral.com/")  # replace with your target website
wait = WebDriverWait(driver, 20)
wait.until(EC.presence_of_element_located((By.XPATH, "//img")))  # wait for all images to load
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
        time.sleep(10)  # wait for the file to load completely
        content = driver.page_source
        filename = link.split('/')[-1]
        with open(os.path.join(dir_name, filename), 'w', encoding='utf-8') as f:
            f.write(content)

# scrape all links on homepage and go one level deep
links = [link.get_attribute("href") for link in driver.find_elements(By.XPATH, "//a")]
for link in links:
    if link and link.startswith("https://www.classcentral.com/"):  # replace with your target website
        # scrape page content
        driver.get(link)
        wait.until(EC.presence_of_element_located((By.XPATH, "//img")))  # wait for all images to load
        html_content = driver.page_source
        filename = link.replace("https://www.classcentral.com/", "").replace("/", "_").strip("_") + '.html'
        with open(os.path.join(dir_name, filename), 'w', encoding='utf-8') as f:
            f.write(html_content)

        # get css and js links and download them
        css_links = [link.get_attribute("href") for link in driver.find_elements(By.XPATH, "//link[@rel='stylesheet']")]
        js_links = [link.get_attribute("src") for link in driver.find_elements(By.XPATH, "//script")]
        for link in css_links + js_links:
            if link:
                driver.get(link)
                time.sleep(10)  # wait for the file to load completely
                content = driver.page_source
                filename = link.split('/')[-1]
                with open(os.path.join(dir_name, filename), 'w', encoding='utf-8') as f:
                    f.write(content)

        # get image links and download them
        image_links = [link.get_attribute("src") for link in driver.find_elements(By.XPATH, "//img")]
        for link in image_links:
            if link:
                driver.get(link)
                time.sleep(10)  # wait for the file to load completely
                content = driver.find_element(By.XPATH, "//body").screenshot_as_png
                filename = link.split('/')[-1]
                with open(os.path.join(dir_name, filename), 'wb') as f:
                    f.write(content)

# quit
