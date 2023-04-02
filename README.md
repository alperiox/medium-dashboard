# A dashboard built with dash

The data is provided by the scraper (in `dev.ipynb` and `scraper.py`), it's in the experimental phase at the moment.

## TODOs

### Dashboard

- [ ] Currently the dataset loads in __every page__. This leads to inefficient data processing.
- [ ] The plots should be rendered in a specific standard. Currently:
  - First two graphs in the publications page is rendered as subplots. Last two is rendered as individual `dcc.Graph` objects
- [ ] Styling of the pages should be improved (some components aligned in a weird way)

### Scraper

- [ ] Scraper should have an individual module for itself. Then this repository should use that module
- [ ] It does not support scraping from author's feed and page.
- [ ] Scraper's page structure support should be extended
  - [ ] Currently, it only scrape data from the publications archive. There are two different page structures for publication archive and it is not able to scrape from one of them. This support should be extended
  - [ ] It should be able to scrape data from author's page
  
### DevOps

- [ ] Dashboard can be updated weekly or daily by setting up a simple cronjob-based workflow
- [ ] Dashboard should be deployed in a platform, ex. [Railway](https://railway.app/)
