import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import logging
from tqdm import tqdm
import time

# ScraperAPI base URL
SCRAPER_API_KEY = '21968e6dd31dc8400bb03dd3792c2657'  # Replace with your ScraperAPI key
SCRAPER_API_URL = f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url="

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_text(text):
    """Clean the extracted text."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?]', '', text)
    return text.strip()

def get_article_summary_selenium(link, retries=3):
    """Scrape article summary using Selenium routed through ScraperAPI."""
    for attempt in range(retries):
        try:
            # Modify link to use ScraperAPI as the proxy
            scraperapi_url = SCRAPER_API_URL + link

            # Set Chrome options for headless scraping
            options = Options()
            options.add_argument("--headless")  # Run headless
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(
                f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            )

            # Initialize WebDriver
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            # Get the page content through ScraperAPI proxy
            driver.get(scraperapi_url)

            # Wait until the body is loaded
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Scroll the page multiple times to load dynamic content
            scroll_page(driver)

            # Wait for content to load
            time.sleep(5)

            # Scrape the page content after cookie consent
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract the actual article content
            paragraphs = soup.find_all('p')
            if not paragraphs:
                logging.warning(f"No <p> tags found at {link}. Trying to fetch divs with class 'content'.")
                paragraphs = soup.find_all('div', class_='content')

            text = ' '.join([para.get_text() for para in paragraphs])
            text = clean_text(text)

            if not text.strip():
                return "No content found."

            # Tokenize into sentences for summarization
            sentences = re.split(r'(?<=[.!?]) +', text)
            summary = []
            word_count = 0
            for sentence in sentences:
                words_in_sentence = len(sentence.split())
                if word_count + words_in_sentence <= 40:
                    summary.append(sentence)
                    word_count += words_in_sentence
                if word_count >= 20:
                    break

            return ' '.join(summary)

        except Exception as e:
            logging.error(f"Error fetching content from {link}: {str(e)}. Retrying {attempt + 1}/{retries}...")
            time.sleep(2)
        finally:
            driver.quit()

    return f"Failed to fetch content from {link} after {retries} attempts."

def scroll_page(driver, retries=5):
    """Scroll down the page multiple times to ensure all content is loaded."""
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(retries):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for the new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            logging.info("Reached bottom of page.")
            break
        last_height = new_height
    else:
        logging.warning("Max scroll retries reached without loading full content.")

# File paths for input and output Excel files
input_file_path = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/Scrapping Input data/Test_data_first.xlsx"
output_file_path = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/Scrapping Output data/Data_syndicate.xlsx"

# Load input data
df = pd.read_excel(input_file_path)

# Check if 'Links' column exists in the Excel file
if 'Links' not in df.columns:
    raise ValueError("The Excel file does not contain a 'Links' column.")

# Process articles and generate summaries
summaries = []

for link in tqdm(df['Links'], total=len(df), desc="Processing Articles"):
    summary = get_article_summary_selenium(link)
    summaries.append(summary)

# Add summaries to DataFrame
df['summary'] = summaries

# Save the output DataFrame to Excel
try:
    df.to_excel(output_file_path, index=False)
    logging.info(f"Summaries saved to {output_file_path}")
except Exception as e:
    logging.error(f"Error saving output Excel file: {str(e)}")

logging.info("Processing complete!")