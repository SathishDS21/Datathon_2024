import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from playwright.sync_api import sync_playwright
import asyncio
from pyppeteer import launch as pyppeteer_launch
import scrapy
from scrapy_splash import SplashRequest
from scrapy.crawler import CrawlerProcess
import fsspec

# Path to the input and output Excel files
input_file = "D:/Python/Scrapping Input data/Test_data_first.xlsx"
output_file = "D:/Python/Scrapping Output data/Data_syndicate.xlsx"

# Custom headers to simulate a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
    'Connection': 'keep-alive'
}

# List of unwanted phrases to filter out
unwanted_phrases = [
    "Sign up", "Reporting by", "Our Standards", "Reuters Trust Principles", "All rights reserved",
    "See here for a complete list", "terms of service", "privacy policy", "cookies"
]

# Tags to blacklist (to remove irrelevant sections)
blacklisted_tags = ['footer', 'nav', 'aside', 'header']


def fetch_content_requests(url):
    """Fetch content using requests."""
    try:
        print(f"Trying requests for URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching content from {url} with requests: {e}")
        return None


def fetch_content_selenium(url, driver):
    """Fetch content using Selenium."""
    try:
        print(f"Trying Selenium for URL: {url}")
        driver.get(url)
        time.sleep(3)
        return driver.page_source
    except Exception as e:
        print(f"Error fetching content from {url} with Selenium: {e}")
        return None


def fetch_content_playwright(url):
    """Fetch content using Playwright."""
    try:
        print(f"Trying Playwright for URL: {url}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state('networkidle')
            content = page.content()
            browser.close()
            return content
    except Exception as e:
        print(f"Error fetching content from {url} with Playwright: {e}")
        return None


async def fetch_content_puppeteer(url):
    """Fetch content using Puppeteer."""
    try:
        print(f"Trying Puppeteer for URL: {url}")
        browser = await pyppeteer_launch(headless=True)
        page = await browser.newPage()
        await page.goto(url, {"waitUntil": "networkidle2"})
        content = await page.content()
        await browser.close()
        return content
    except Exception as e:
        print(f"Error fetching content from {url} with Puppeteer: {e}")
        return None


class ScrapySpider(scrapy.Spider):
    """Scrapy spider that integrates with Splash."""
    name = "article_spider"

    def __init__(self, url=None, *args, **kwargs):
        super(ScrapySpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 3}, headers=headers)

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        article_text = []
        paragraphs = soup.find_all('p')
        for paragraph in paragraphs:
            text = paragraph.get_text()
            if not any(phrase in text for phrase in unwanted_phrases):
                article_text.append(text)
        return {'Article Content': ' '.join(article_text)}


def fetch_content_scrapy_splash(url):
    """Fetch content using Scrapy-Splash."""
    process = CrawlerProcess(settings={
        'SPIDER_MODULES': ['scraper.spiders'],
        'SPLASH_URL': 'http://localhost:8050',
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        },
        'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
        'HTTPCACHE_STORAGE': 'scrapy_splash.SplashAwareFSCacheStorage',
        'LOG_ENABLED': False  # Disable logging for cleaner output
    })

    process.crawl(ScrapySpider, url=url)
    process.start()  # Blocks until the crawling is finished


def parse_article_content(html_content):
    """Extract article content from the rendered HTML using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove blacklisted tags (footer, nav, etc.)
    for tag in blacklisted_tags:
        [s.extract() for s in soup.find_all(tag)]

    article_text = []

    # Target the main article section by looking for common article tags and classes
    main_content = soup.find('article')
    if not main_content:
        main_content = soup.find('div', {'class': 'ArticleBodyWrapper'})
    if not main_content:
        main_content = soup.find('div', {'class': 'article-body'})
    if not main_content:
        main_content = soup.find('section')

    if not main_content:
        print("Could not find the main article container, extracting <p> tags directly.")
        paragraphs = soup.find_all('p')
        if paragraphs:
            return ' '.join([p.get_text() for p in paragraphs])

    # Extract paragraphs from the main content and filter out unwanted phrases
    if main_content:
        for paragraph in main_content.find_all('p'):
            text = paragraph.get_text()
            if not any(phrase in text for phrase in unwanted_phrases):  # Filter out unwanted paragraphs
                article_text.append(text)

    return ' '.join(article_text) if article_text else "No content found"


# Main Scraping Workflow using pandas
try:
    input_df = pd.read_excel(input_file)  # Directly read Excel using pandas
except UnicodeDecodeError as e:
    print(f"Unicode decoding error with Excel file: {e}")
    input_df = pd.read_excel(input_file, encoding='ISO-8859-1')  # Try alternative encoding

output_data = []

# Initialize Selenium WebDriver
selenium_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=webdriver.ChromeOptions())

for index, row in input_df.iterrows():
    url = row['Links']
    content = None
    try:
        print(f"Processing URL: {url}")

        # Try each scraping method one by one
        content = fetch_content_requests(url)
        if not content:
            content = fetch_content_selenium(url, selenium_driver)
        if not content:
            content = fetch_content_playwright(url)
        if not content:
            content = asyncio.run(fetch_content_puppeteer(url))
        if not content:
            fetch_content_scrapy_splash(url)  # Try Scrapy-Splash if others fail

        if content:
            article_content = parse_article_content(content)
            if not article_content.strip():
                print(f"No content found for URL: {url}")
            output_data.append({'URL': url, 'Article Content': article_content})
        else:
            output_data.append({'URL': url, 'Article Content': 'Error: Failed to load content'})

    except Exception as e:
        print(f"Error processing {url}: {e}")
        output_data.append({'URL': url, 'Article Content': f"Error scraping content: {str(e)}"})

# Close Selenium WebDriver
selenium_driver.quit()

# Save output to Excel using FSSpec for efficient I/O
with fsspec.open(output_file, 'wb') as f:
    output_df = pd.DataFrame(output_data)
    output_df.to_excel(f, index=False)

print(f"Scraping complete. Data saved to {output_file}")
