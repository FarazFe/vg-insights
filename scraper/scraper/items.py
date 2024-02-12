# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScraperItem(scrapy.Item):
    steam_id = scrapy.Field()
    developers = scrapy.Field()
    publishers = scrapy.Field()
    first_release_date = scrapy.Field()
    price = scrapy.Field()
    genres = scrapy.Field()
    tags = scrapy.Field()
    languages = scrapy.Field()

    avg_6_months_price = scrapy.Field()
    short_description = scrapy.Field()

    avg_playtime = scrapy.Field()
    med_playtime = scrapy.Field()
    max_players_24h = scrapy.Field()
    players_latest = scrapy.Field()
    players_latest_time = scrapy.Field()
# class PriceInfoItem(scrapy.Item):
#     avg6Months = scrapy.Field()
#
#
# class MetaItem(scrapy.Item):
#     shortDescription = scrapy.Field()


# class QuickStatsItem(scrapy.Item):
#     avg_playtime = scrapy.Field()
#     med_playtime = scrapy.Field()
#     max_players_24h = scrapy.Field()
#     players_latest = scrapy.Field()
#     players_latest_time = scrapy.Field()
