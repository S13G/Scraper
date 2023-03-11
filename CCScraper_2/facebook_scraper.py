# Import the necessary libraries
from itertools import zip_longest
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
chrome_options.add_argument("--headless")
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
email = "ayflix0@gmail.com"
password = "S13gd0ma1n£"
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

# Loop through all matching tags and sentences
for tag in matching_tags:
    for sentence in tag.get_text().split('.'):
        # Convert sentence to lowercase and find the index of the keyword
        sentence_lower = sentence.strip().lower()
        keyword_index = sentence_lower.find(keywords.lower())
        # If the keyword exists in the sentence
        if keyword_index != -1:
            # Extract the part of the sentence from the keyword to the end
            sentence_from_keyword = sentence[keyword_index:]
            # Check if the sentence contains any positive keywords
            if any(word.strip().lower() in sentence_from_keyword.strip().lower() for word in positive_words):
                clean_sentence = sentence_from_keyword.strip().replace('\n', ' ').replace('\t', ' ')
                clean_sentence = re.sub(r'[^\w\s]', '', clean_sentence)
                positive_sentences.append(clean_sentence)
            # Check if the sentence contains any negative keywords
            elif any(word.strip().lower() in sentence_from_keyword.strip().lower() for word in negative_words):
                clean_sentence = sentence_from_keyword.strip().replace('\n', ' ').replace('\t', ' ')
                clean_sentence = re.sub(r'[^\w\s]', '', clean_sentence)
                negative_sentences.append(clean_sentence)
            # If the sentence doesn't contain any positive or negative keywords, add it to "other" sentences
            else:
                clean_sentence = sentence_from_keyword.strip().replace('\n', ' ').replace('\t', ' ')
                clean_sentence = re.sub(r'[^\w\s]', '', clean_sentence)
                other_sentences.append(clean_sentence)

# Create a pandas DataFrame for each category of sentences
positive_df = pd.DataFrame({'Positive Keywords': positive_sentences})
negative_df = pd.DataFrame({'Negative Keywords': negative_sentences})
other_df = pd.DataFrame({'Other Keywords': other_sentences})

# Concatenate the DataFrames and write to CSV and XLSX files
df = pd.concat([positive_df, negative_df, other_df], axis=1)
df.to_csv('results.csv', index=False)
with pd.ExcelWriter('results.xlsx') as writer:
    df.to_excel(writer, sheet_name='Sheet1', index=False)

# Close the Selenium driver
driver.quit()
