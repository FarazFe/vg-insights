import scrapy
from ..items import ScraperItem
from ..utils import get_top_steam_games
from ..config import SITE_TOKEN

class VGInsightsSpider(scrapy.Spider):
    name = "vginsights"

    def __init__(self):
        self.headers = {
            'Host': 'vginsights.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Authorization': SITE_TOKEN,
            'Connection': 'keep-alive',
            'Cookie': '_ga_Y6GXH6BJC6=GS1.1.1707651146.1.1.1707654037.0.0.0; _ga=GA1.1.15278639.1707651146; _gid=GA1.2.90886740.1707651148; _hjSessionUser_2188705=eyJpZCI6IjdhM2FmYjI4LWJmMDEtNTcwOS1iZWY5LTVmYmE1NTZhNmVmMSIsImNyZWF0ZWQiOjE3MDc2NTExNDc2NjUsImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_2188705=eyJpZCI6ImFlNWMzY2YxLTRhYzUtNGI2Zi1hNDEzLTkzY2Q3ODlkMjFlNyIsImMiOjE3MDc2NTExNDc2NjYsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0='
        }
        super().__init__()

    def start_requests(self):
        steam_ids = get_top_steam_games(5)

        for steam_id in steam_ids:
            url = 'https://vginsights.com/api/v1/game/{}/'.format(steam_id)
            yield scrapy.Request(url=url, callback=self.parse_main, headers=self.headers)

    def parse_main(self, response):
        data = response.json()

        item = ScraperItem()
        item['steam_id'] = data['steam_id']
        item['developers'] = data['developers']
        item['publishers'] = data['publishers']
        item['first_release_date'] = data['released']
        item['price'] = data['price']
        item['tags'] = data['tag_names']
        item['languages'] = data['languages']

        steam_id = data['steam_id']
        yield scrapy.Request('https://vginsights.com/api/v1/game/{}/price-info/'.format(steam_id), meta={'item': item},
                             callback=self.parse_price, headers=self.headers)

    def parse_price(self, response):
        item = response.meta['item']
        data = response.json()
        item['avg_6_months_price'] = data['avg6Months']

        # Send request for description
        yield scrapy.Request('https://vginsights.com/api/v1/game/{}/meta/'.format(item['steam_id']),
                             meta={'item': item},
                             callback=self.parse_game_meta, headers=self.headers)

    def parse_game_meta(self, response):
        item = response.meta['item']
        data = response.json()
        item['short_description'] = data['meta']['shortDescription']

        # Send request for quick stats
        yield scrapy.Request('https://vginsights.com/api/v1/game/{}/quick-stats'.format(item['steam_id']),
                             meta={'item': item},
                             callback=self.parse_quick_stats, headers=self.headers)

    def parse_quick_stats(self, response):
        item = response.meta['item']
        data = response.json()
        item['avg_playtime'] = data['avg_playtime']
        item['med_playtime'] = data['med_playtime']
        item['players_latest'] = data['players_latest']
        item['players_latest_time'] = data['players_latest_time']

        yield item

        yield scrapy.Request('https://vginsights.com/api/v1/game/{}/regional-info/xlsx'.format(item['steam_id']),
                             meta={'prefix': 'player_insights', 'steam_id': item['steam_id']},
                             callback=self.parse_save_file, headers=self.headers)

        yield scrapy.Request('https://vginsights.com/api/v1/game/{}/history/xlsx'.format(item['steam_id']),
                             meta={'prefix': 'historical_data', 'steam_id': item['steam_id']},
                             callback=self.parse_save_file, headers=self.headers)

    def parse_save_file(self, response):
        file_prefix = response.meta['prefix']
        steam_id = response.meta['steam_id']

        with open('excel_files/{}/{}.xlsx'.format(file_prefix, steam_id), 'wb') as f:
            f.write(response.body)
