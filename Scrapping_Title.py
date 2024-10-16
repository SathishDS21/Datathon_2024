import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup  # Add BeautifulSoup for parsing
import time


# Set the input and output file paths
input_file_path = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/Scrapping Input data/Test_data_first.xlsx"
output_file_path = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/Scrapping Output data/Data_output.xlsx"


def configure_firefox():
    # Set up Selenium with Firefox in headless mode
    options = Options()
    options.headless = True

    # Set the correct binary location of Firefox on your system
    options.binary_location = '/Applications/Firefox.app/Contents/MacOS/firefox'  # Update this path for your system

    # Set the path to geckodriver (Firefox WebDriver)
    service = Service(executable_path='/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/geckodriver')

    # Initialize the Firefox driver
    driver = webdriver.Firefox(service=service, options=options)
    return driver


def scrape_with_selenium(url):
    driver = configure_firefox()
    title = ""
    article_body = ""

    try:
        # Open the article URL
        driver.get(url)
        time.sleep(5)  # Wait for the page to load fully

        # Scrape the content using BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract the title
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.text

        # Extract the article text
        article_body = " ".join([p.text for p in soup.find_all('p')])

    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()

    return title, article_body


def scrape_and_save_to_excel(input_file_path, output_file_path):
    # Read the input Excel file containing URLs
    df = pd.read_excel(input_file_path)

    # Create empty lists to store results
    titles = []
    bodies = []

    # Loop over each URL in the input file
    for url in df['Links']:  # Assuming 'Links' is the column with URLs
        print(f"Scraping URL: {url}")
        title, body = scrape_with_selenium(url)
        titles.append(title)
        bodies.append(body)

    # Create a DataFrame to store the results
    result_df = pd.DataFrame({
        'URL': df['Links'],
        'Title': titles,
        'Body': bodies
    })

    # Save the results to an Excel file
    result_df.to_excel(output_file_path, index=False)
    print(f"Scraping completed and saved to {output_file_path}")


# Start the scraping process
scrape_and_save_to_excel(input_file_path, output_file_path)