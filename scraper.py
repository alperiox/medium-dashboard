import datetime
import logging
import os
from datetime import timedelta

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG)


class PublicationScraper:
    """
    A simple scraper that connects to the publication's archive
    and collect all the articles published this month
    """

    def __init__(self, publication: str, rollback=None, **kwargs):
        self.publication_url = publication
        self.archive_url = os.path.join(self.publication_url, "archive")
        self.current_date = datetime.date.today()

        self.target_urls = []
        self.target_dates = []
        self.pages = []

        self.data = {}

        self.check_archive()
        if not self.archive_available:
            raise NotImplementedError("Scraping from the profile page (without archive) is not supported.")

        if rollback:
            for m in range(1, rollback + 2):
                date = self.current_date.replace(day=1) - timedelta(1 * 30 * m)
                target_url = os.path.join(self.archive_url, str(date.year), f"{str(date.month):0^2}")
                print("date:", date)
                print("url:", target_url)

                self.target_dates.append(date)
                self.target_urls.append(target_url)

        for date, url in zip(self.target_dates, self.target_urls):
            logging.info(f"Constructed the target url: {url}")
            req = requests.get(url)
            logging.info(f"Sent the GET request, status code: {req.status_code}")

            print("req.url", req.url)
            print("os.path.join(self.archive_url, str(date.year))", os.path.join(self.archive_url, str(date.year)))

            if req.url == os.path.join(self.archive_url, str(date.year)):
                raise NotImplementedError(
                    "Scraping just from the year is not implemented yet. (URL: %s)" % (self.publication_url)
                )

            page = BeautifulSoup(req.content, "html.parser")
            logging.info("Initialized the beautifulsoup")
            self.pages.append(page)

    def check_archive(self):
        r = requests.get(self.archive_url)
        if "PAGE NOT FOUND" in r.text and "404" in r.text:
            self.archive_available = False
        else:
            self.archive_available = True

    def scrape(self):
        for page, date, url in zip(self.pages, self.target_dates, self.target_urls):
            print("current date:", date)
            print("current url:", url)
            posts = self.get_posts(page)
            data = self.get_data(posts)
            self.data[date] = data
        return self.data

    def scrape_profile(self):
        """
        It should be noted that the Medium sends a POST request to the -author_medium_url-/_/batch with some authentication/bot analysis
        headers. So it's highly possible to reverse-engineer the API and imitate a real client to collect the data.
        """
        raise NotImplementedError("Not implemented yet.")

    def get_posts(self, page) -> list[str]:
        posts = page.find_all("div", {"streamItem--postPreview"})
        return posts

    def get_data(self, posts) -> list[dict]:
        samples = []
        for post in posts:
            author = post.find("div", {"class": "postMetaInline-authorLockup"}).find("a").text
            uicaption = post.find("div", {"class": "ui-caption"})
            date = uicaption.find("a").find("time")["datetime"]
            reading_time = uicaption.find("span", {"class": "readingTime"})["title"]

            article_content = post.find("div", {"class": "postArticle-content"})
            section = article_content.select("section.section > div.section-content > div.section-inner")
            title = section[0].select("h3").text
            post_url = article_content.parent["href"]
            preview_image_url = article_content.find("figure").find("img")["src"]
            claps = post.find("div", {"class": "multirecommend"}).find_all("span")[-1].text

            sample = {
                "author": author,
                "date": date,
                "reading_time": reading_time,
                "post_url": post_url,
                "title": title,
                "preview_image_url": preview_image_url,
                "claps": claps,
            }

            sample = self.post_process(sample)

            samples.append(sample)

        return samples

    def post_process(self, sample: dict):
        sample["date"] = sample["date"].split("T")[0]
        sample["reading_time"] = " ".join(sample["reading_time"].split()[:-1])
        sample["post_url"] = sample["post_url"].split("?source=collection_archive")[0]
        return sample


class MediumScraper:
    def __init__(self, publications, suppress=False, **publication_scraper_kwargs):
        self.publications = publications
        self.archives = list(map(lambda x: os.path.join(x, "archive"), publications))
        self.scrapers = []
        self.data = {}
        for publication in publications:
            if suppress:
                try:
                    scraper = PublicationScraper(publication, **publication_scraper_kwargs)
                except Exception as e:
                    print("An error occurred:", e)
                    print("Removing the publication: %s" % (publication))
                    self.publications.remove(publication)
            else:
                scraper = PublicationScraper(publication, **publication_scraper_kwargs)

            self.scrapers.append((publication, scraper))

    def scrape(self):
        for pub, scraper in self.scrapers:
            data = scraper.scrape()
            if pub in self.data.keys():
                self.data[pub].append(data)
            else:
                self.data[pub] = []


if __name__ == "__main__":
    scraper = PublicationScraper("https://towardsdatascience.com/", rollback=1)
    data = scraper.scrape()
