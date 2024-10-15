from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Function to scrape content using Selenium
def scrape_with_selenium(url):
    # Set up the Chrome WebDriver with necessary options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Open the page
        driver.get(url)

        # Wait for the headline to be present (Use an appropriate selector, e.g., By.CSS_SELECTOR or By.XPATH)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )

        # Extract headline (use another strategy if h1 isn't found)
        headline = driver.find_element(By.TAG_NAME, 'h1').text

        # Wait for the article body content to be present (adjust if necessary)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'article-body__content'))
        )

        # Extract article content
        article_body = driver.find_element(By.CLASS_NAME, 'article-body__content').text

        return headline, article_body

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    return None


# Example usage
if __name__ == "__main__":
    url = 'https://timesofindia.indiatimes.com'
    result = scrape_with_selenium(url)

    if result:
        headline, article_text = result
        print("Headline:", headline)
        print("\nArticle Text:", article_text)
    else:
        print("Failed to scrape the content.")