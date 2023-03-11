# Import the necessary libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

# setting up the Selenium driver with options
chrome_options = Options()

# uncomment this line if you want the code to run without browser interface
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

# Ask the user for the keywords
keywords = input("Enter the keywords to search for: ")

# Prompt the user for positive and negative words
positive_words = input(
    "Enter the positive words (comma-separated): ").split(",")
negative_words = input(
    "Enter the negative words (comma-separated): ").split(",")

url = "https://www.facebook.com"

driver.get(url)

# Find the search box and enter the keywords
# Login to Facebook first
email = input("Enter your Facebook email: ")
password = input("Enter your Facebook password: ")
email_box = driver.find_element(By.ID, "email")
password_box = driver.find_element(By.ID, "pass")
email_box.send_keys(email)
password_box.send_keys(password + Keys.RETURN)
time.sleep(5)

# Find the search box after logging in
search_box = driver.find_element(
    By.CSS_SELECTOR, 'input[aria-label="Search Facebook"]')

# Press enter to perform the search
search_box.send_keys(keywords + Keys.RETURN)

# Wait for the page to load
time.sleep(10)

# Get the HTML content of the page
html_content = driver.page_source
soup = BeautifulSoup(html_content, "html.parser")

# Find all the div elements in the page
divs = soup.find_all("div")

# Search for the entered keywords in all divs with a specific prefix
matching_tags = []
for tag in soup.find_all():
    if tag.get_text().lower().startswith(keywords.lower()):
        matching_tags.append(tag)

# Extract matching sentences and store them in appropriate files
positive_sentences = []
negative_sentences = []
other_sentences = []

for tag in matching_tags:
    for sentence in tag.get_text().split('.'):
        if any(word.strip().lower() in sentence.strip().lower() for word in positive_words):
            clean_sentence = sentence.strip().replace('\n', ' ').replace('\t', ' ')
            clean_sentence = re.sub(r'[^\w\s]', '', clean_sentence)
            positive_sentences.append(clean_sentence)
        elif any(word.strip().lower() in sentence.strip().lower() for word in negative_words):
            clean_sentence = sentence.strip().replace('\n', ' ').replace('\t', ' ')
            clean_sentence = re.sub(r'[^\w\s]', '', clean_sentence)
            negative_sentences.append(clean_sentence)
        else:
            clean_sentence = sentence.strip().replace('\n', ' ').replace('\t', ' ')
            clean_sentence = re.sub(r'[^\w\s]', '', clean_sentence)
            other_sentences.append(clean_sentence)

# Create a pandas DataFrame for each category of sentences
positive_df = pd.DataFrame({'Sentence': positive_sentences})
negative_df = pd.DataFrame({'Sentence': negative_sentences})
other_df = pd.DataFrame({'Sentence': other_sentences})

# Write each DataFrame to a separate sheet in an Excel file
with pd.ExcelWriter('results.xlsx') as writer:
    positive_df.to_excel(writer, sheet_name='Positive', index=False)
    negative_df.to_excel(writer, sheet_name='Negative', index=False)
    other_df.to_excel(writer, sheet_name='Other', index=False)

# Close the Selenium driver
driver.quit()
