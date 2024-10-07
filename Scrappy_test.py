import pandas as pd
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
import re
from tqdm import tqdm  # For progress bar
import logging

# Download necessary resources for sentence tokenization
nltk.download('punkt')

# Setup logging for better debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_text(text):
    """
    Clean the extracted text by removing unnecessary characters and extra spaces.
    """
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with a single space
    text = re.sub(r'[^\w\s.,!?]', '', text)  # Remove unwanted characters
    return text.strip()

def get_article_summary(link):
    """
    Extract and summarize an article from the provided link.
    """
    try:
        # Send a GET request to fetch the article with a timeout of 10 seconds
        response = requests.get(link, timeout=10)
        response.raise_for_status()  # Check for request errors

        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Try extracting text from <p>, <div>, or <article> tags
        paragraphs = soup.find_all('p') or soup.find_all('div') or soup.find_all('article')

        # Join and clean the extracted text
        text = ' '.join([para.get_text() for para in paragraphs])
        text = clean_text(text)

        # If the text is empty, return a message
        if not text:
            logging.warning(f"No content found for link: {link}")
            return "No content found."

        # Tokenize the text into sentences
        sentences = sent_tokenize(text)

        # Adjust summary length based on total length of the article
        total_words = len(text.split())
        summary_length = min(50, max(20, total_words // 10))  # Dynamic summary length

        # Summarize the content by selecting the first few sentences
        summary = []
        word_count = 0
        for sentence in sentences:
            words_in_sentence = len(sentence.split())
            if word_count + words_in_sentence <= summary_length:
                summary.append(sentence)
                word_count += words_in_sentence
            if word_count >= 20:  # Ensure at least 20 words in the summary
                break

        # Join the selected sentences into a final summary
        return ' '.join(summary)

    except requests.exceptions.Timeout:
        logging.error(f"Timeout error for URL: {link}")
        return "Error: Timeout"
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching content from URL {link}: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logging.error(f"Unexpected error for URL {link}: {e}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Define file paths for input and output
    input_file_path = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/Scrapping Input data/Test_data_first.xlsx"
    output_file_path = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/Scrapping Output data/Data_syndicate1.xlsx"

    # Read the Excel file containing the links
    df = pd.read_excel(input_file_path)

    # Check if the 'Links' column exists in the Excel file
    if 'Links' not in df.columns:
        raise ValueError("The Excel file does not contain a 'Links' column.")

    # Initialize an empty list to store the summaries
    summaries = []

    # Process each link using tqdm for progress display
    for link in tqdm(df['Links'], total=len(df), desc="Processing Articles"):
        summary = get_article_summary(link)
        summaries.append(summary)

    # Add the summaries to the DataFrame
    df['summary'] = summaries

    # Save the DataFrame with summaries to the output Excel file
    try:
        df.to_excel(output_file_path, index=False)
        logging.info(f"Summaries saved to {output_file_path}")
    except Exception as e:
        logging.error(f"Error saving output Excel file: {e}")
        raise ValueError(f"Error saving output Excel file: {e}")

    logging.info("Processing complete!")