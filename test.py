from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup  # Add BeautifulSoup for parsing
import time


def scrape_with_selenium(url):
    # Set up Selenium with Firefox in headless mode
    options = Options()
    options.headless = True

    # Set the correct binary location of Firefox on your system
    options.binary_location = '/Applications/Firefox.app/Contents/MacOS/firefox'  # Update this path for your system

    # Update this path to the location where geckodriver is installed on your machine
    service = Service(executable_path='/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/geckodriver')

    driver = webdriver.Firefox(service=service, options=options)

    try:
        # Open the article URL
        driver.get(url)
        time.sleep(5)  # Wait for the page to load fully

        # Scrape the content using BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract title
        title = soup.find('title').text
        print(f"Title: {title}")

        # Extract the article text (adjust based on page structure)
        article_body = " ".join([p.text for p in soup.find_all('p')])
        print(f"Body: {article_body[:500]}...")  # Print first 500 characters

    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()


# Prompt user for input
url = input("Enter a Reuters article link: ")
scrape_with_selenium(url)