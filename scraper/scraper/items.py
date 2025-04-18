# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemadapter import ItemAdapter


class ScraperItem(scrapy.Item):
    steam_id = scrapy.Field()
    developers = scrapy.Field()
    publishers = scrapy.Field()
    first_release_date = scrapy.Field()
    price = scrapy.Field()
    genres = scrapy.Field()
    tags = scrapy.Field()
    languages = scrapy.Field()
    short_description = scrapy.Field()
    title = scrapy.Field()
    slug = scrapy.Field()

    avg_6_months_price = scrapy.Field()
    avg_playtime = scrapy.Field()
    med_playtime = scrapy.Field()
    max_players_24h = scrapy.Field()
    players_latest = scrapy.Field()
    players_latest_time = scrapy.Field()

class QuickStatsItem(scrapy.Item):
    steam_id = scrapy.Field()
    avg_playtime = scrapy.Field()
    med_playtime = scrapy.Field()
    max_players_24h = scrapy.Field()
    players_latest = scrapy.Field()
    players_latest_time = scrapy.Field()
    daily_active_users = scrapy.Field()
    monthly_active_users = scrapy.Field()
    rating = scrapy.Field()
    revenue_vgi = scrapy.Field()
    units_sold_vgi = scrapy.Field()
    wishlist_count = scrapy.Field()

class PlayerInsightsItem(scrapy.Item):
    steam_id = scrapy.Field()
    countries = scrapy.Field()
    regions = scrapy.Field()
    playtime = scrapy.Field()
    games = scrapy.Field()
    wishlists = scrapy.Field()

class HistoricalDataItem(scrapy.Item):
    steam_id = scrapy.Field()
    members = scrapy.Field()
    wishlist_count = scrapy.Field()
    players_max = scrapy.Field()
    players_avg = scrapy.Field()
    units = scrapy.Field()
    units_increase = scrapy.Field()
    revenue_sum = scrapy.Field()
    revenue_increase = scrapy.Field()
    reviews = scrapy.Field()
    rating = scrapy.Field()
    daily_active_users = scrapy.Field()
    monthly_active_users = scrapy.Field()
    price = scrapy.Field()

class PlayerOverlapItem(scrapy.Item):
    steam_id = scrapy.Field()
    name = scrapy.Field()
    released = scrapy.Field()
    genres = scrapy.Field()
    median_playtime = scrapy.Field()
    owner_overlap = scrapy.Field()
    owner_overlap_percentage = scrapy.Field()
    owner_overlap_index = scrapy.Field()
    mau_overlap = scrapy.Field()
    mau_overlap_percentage = scrapy.Field()
    mau_overlap_index = scrapy.Field()
    wishlist_overlap = scrapy.Field()
    wishlist_overlap_percentage = scrapy.Field()
    wishlist_overlap_index = scrapy.Field()

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
