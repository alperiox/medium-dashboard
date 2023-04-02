import os

from dotenv import load_dotenv

# data processing
# Data Analysis
import pandas as pd

from medium_scraper import ProfileScraper


def extract(urls):
    scraper = ProfileScraper()
    dataset = {}
    for url in urls:
        print("Scraping url:", url)
        data = scraper.extract(url)
        dataset[url] = data

    data = []
    for author_url, posts in dataset.items():
        for post in posts:
            post["author_url"] = author_url
            data.append(post)

    dataframe = pd.DataFrame(data)

    dataset_name = "raw_dataset.csv"

    dataframe.to_csv(os.path.join(DATASET_PATH, dataset_name), index=False)

    return dataframe


if __name__ == "__main__":
    load_dotenv()
    DATASET_PATH = os.getenv("DATASET_PATH")

    with open("authors.txt", "r") as f:
        author_urls = f.readlines()

    author_urls = list(map(lambda s: s.strip().strip("\n"), author_urls))

    extract(author_urls)
