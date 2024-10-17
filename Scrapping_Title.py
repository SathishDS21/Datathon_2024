import random
import cloudscraper
from bs4 import BeautifulSoup

# Predefined list of possible locations
possible_locations = ['Washington, D.C.', 'Tehran, Iran', 'Moscow, Russia', 'London, UK', 'New York, USA']

def assign_random_location():
    """Assign a random location from a predefined list."""
    return random.choice(possible_locations)

def scrape_with_cloudscraper(url):
    """Scrape using CloudScraper and target the main article section."""
    try:
        print(f"Attempting with CloudScraper...")

        # Define the headers to simulate a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Create a CloudScraper instance
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, headers=headers)

        # Check if the response was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML response with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract the title from the <h1> tag
            title = soup.find('h1')
            if title:
                title = title.text.strip()
            else:
                print("Title not found!")
                return None

            # Extract content only from the main article (assuming it's inside <article>)
            main_article = soup.find('article')
            if main_article:
                paragraphs = main_article.find_all('p')
                content = " ".join([p.text.strip() for p in paragraphs])
            else:
                print("Main article content not found!")
                return None

            # Assign a random location
            location = assign_random_location()

            # Return the scraped data
            return {"title": title, "content": content, "location": location}
        else:
            print(f"CloudScraper failed with status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error with CloudScraper: {e}")
        return None

# URL of the Reuters article
url = 'https://www.reuters.com/world/us-asks-iran-stop-selling-drones-russia-ft-2023-08-16/'

# Start the scraping process
article_data = scrape_with_cloudscraper(url)

# Output the result
if article_data:
    print("\nScraped Data:")
    print(f"Title: {article_data['title']}")
    print(f"Content: {article_data['content']}")  # Print the full content of the article
    print(f"Location: {article_data['location']}")
else:
    print("Failed to scrape the article.")