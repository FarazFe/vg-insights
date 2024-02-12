# VGInsight-Scraper

A Scraper for analysing VGInsight.com

## Installation

```bash
$ git clone https://github.com/FarazFe/VGInsight.git
$ cd vg-insights
$ pip install -r requirements.txt
```

## Usage

```bash
$ cd scraper
```

```bash
$ scrapy crawl vginsights -o output.json
```
Don't forget to put the JWT token inside config.py file after login.
## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.