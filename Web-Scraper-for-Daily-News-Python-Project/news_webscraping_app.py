from loguru import logger
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# Function to scrape news headlines
def scrape_news(url):
    logger.info(f"Scraping news from {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.content, "html.parser")

        # Modify selectors based on the website's structure
        headlines = soup.select("h2")  # Example selector for headlines

        news = [{"headline": headline.get_text(strip=True)} for headline in headlines]
        logger.info(f"Scraped {len(news)} headlines.")
        return news
    except Exception as e:
        logger.error(f"Error scraping news: {e}")
        return []


# Function to save news to a CSV file
def save_news_csv(news, file_name="news.csv"):
    try:
        logger.info(f"Saving news to {file_name}")
        df = pd.DataFrame(news)
        df.to_csv(file_name, index=False)
        logger.success(f"News saved to {file_name}")
    except Exception as e:
        logger.error(f"Error saving news to CSV: {e}")


# Function to save news to a JSON file
def save_news_json(news, file_name="news.json"):
    try:
        logger.info(f"Saving news to {file_name}")
        with open(file_name, "w") as f:
            json.dump(news, f, indent=4)
        logger.success(f"News saved to {file_name}")
    except Exception as e:
        logger.error(f"Error saving news to JSON: {e}")

# Main function
if __name__ == "__main__":
    # Configuration
    news_url = "https://www.thehindu.com/"  # Replace with the target news website
    csv_file = "news.csv"
    json_file = "news.json"

    # Scrape news
    news_data = scrape_news(news_url)

    # Save news to files
    save_news_csv(news_data, csv_file)
    save_news_json(news_data, json_file)
