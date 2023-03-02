# works but has bugs

import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# set up selenium driver
driver = webdriver.Chrome()
driver.get("https://www.classcentral.com/")  # replace with your target website

# create directory to store files
dir_name = 'scraped_data'
if not os.path.exists(dir_name):
    os.makedirs(dir_name)

# get html content and write to file
wait = WebDriverWait(driver, 20)
wait.until(EC.presence_of_all_elements_located((By.XPATH, "//img")))  # wait for all images to load
html_content = driver.page_source
with open(os.path.join(dir_name, 'homepage.html'), 'w', encoding='utf-8') as f:
    f.write(html_content)

# get css and js links and download them
css_links = [link.get_attribute("href") for link in driver.find_elements(By.XPATH, "//link[@rel='stylesheet']")]
js_links = [link.get_attribute("src") for link in driver.find_elements(By.XPATH, "//script")]
for link in css_links + js_links:
    if link:
        driver.get(link)
        time.sleep(6)  # wait for the file to load completely
        content = driver.page_source
        filename = link.split('/')[-1]
        with open(os.path.join(dir_name, filename), 'w', encoding='utf-8') as f:
            f.write(content)

# scrape all links on homepage and linked pages
links = [link.get_attribute("href") for link in driver.find_elements(By.XPATH, "//a")]
for link in links:
    if link and link.startswith("https://www.classcentral.com/"):  # replace with your target website
        # scrape page content
        driver.get(link)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, "//img")))  # wait for all images to load
        # get html content and write to file
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
                time.sleep(6)  # wait for the file to load completely
                content = driver.page_source
                filename = link.split('/')[-1]
                with open(os.path.join(dir_name, filename), 'w', encoding='utf-8') as f:
                    f.write(content)

        # get image links and download them
        image_links = [link.get_attribute("src") for link in driver.find_elements(By.XPATH, "//img")]
        for link in image_links:
            if link:
                driver.get(link)
                time.sleep(4)  # wait for the file to load completely
                content = driver.page_source
                filename = link.split('/')[-1]
                with open(os.path.join(dir_name, filename), 'wb') as f:
                    f.write(content)

        # go one level deep and scrape linked pages
        sublinks = [sublink.get_attribute("href") for sublink in driver.find_elements(By.XPATH, "//a")]
        for sublink in sublinks:
            if sublink and sublink.startswith(
                    "https://www.classcentral.com/"):  # replace with your target website
                driver.get(sublink)
                wait.until(EC.presence_of_element_located((By.XPATH, "//img")))  # wait
                # get html content and write to file
                html_content = driver.page_source
                filename = link.replace("https://www.classcentral.com/", "").replace("/", "_").strip("_") + '.html'
                with open(os.path.join(dir_name, filename), 'w', encoding='utf-8') as f:
                    f.write(html_content)

                # get css and js links and download them
                css_links = [link.get_attribute("href") for link in
                             driver.find_elements(By.XPATH, "//link[@rel='stylesheet']")]
                js_links = [link.get_attribute("src") for link in driver.find_elements(By.XPATH, "//script")]
                for link in css_links + js_links:
                    if link:
                        driver.get(link)
                        time.sleep(6)  # wait for the file to load completely
                        content = driver.page_source
                        filename = link.split('/')[-1]
                        with open(os.path.join(dir_name, filename), 'w', encoding='utf-8') as f:
                            f.write(content)

                # get image links and download them
                image_links = [link.get_attribute("src") for link in driver.find_elements(By.XPATH, "//img")]
                for link in image_links:
                    if link:
                        driver.get(link)
                        time.sleep(4)  # wait for the file to load completely
                        content = driver.page_source
                        filename = link.split('/')[-1]
                        with open(os.path.join(dir_name, filename), 'wb') as f:
                            f.write(content)
