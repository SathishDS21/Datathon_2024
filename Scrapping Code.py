import pandas as pd
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
import re
from tqdm import tqdm

nltk.download('punkt')

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?]', '', text)
    return text.strip()

def get_article_summary(link):

    try:
        response = requests.get(link)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])

        text = clean_text(text)

        if not text.strip():
            return "No content found."

        sentences = sent_tokenize(text)

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
        return f"Error fetching content: {str(e)}"

input_file_path = "D:/Python/Scrapping Input data/Test_data_first.xlsx"
output_file_path = "D:/Python//Scrapping Output data/Data_syndicate.xlsx"

df = pd.read_excel(input_file_path)

if 'Links' not in df.columns:
    raise ValueError("The Excel file does not contain a 'Links' column.")

summaries = []

for link in tqdm(df['Links'], total=len(df), desc="Processing Articles"):
    summary = get_article_summary(link)
    summaries.append(summary)

df['summary'] = summaries

try:
    df.to_excel(output_file_path, index=False)
    print(f"Summaries saved to {output_file_path}\n")
except Exception as e:
    raise ValueError(f"Error saving output Excel file: {e}")

print("Processing complete!")