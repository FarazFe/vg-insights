import scrapy
import logging
from ..items import ScraperItem, QuickStatsItem, PlayerInsightsItem, HistoricalDataItem, PlayerOverlapItem
from ..utils import get_top_steam_games
from ..config import SITE_TOKEN

class VGInsightsSpider(scrapy.Spider):
    name = "vginsights"

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Authorization': SITE_TOKEN,
        }
        self.games_processed = 0
        super().__init__()

    def start_requests(self):
        steam_ids = [1200, 1510, 570]  # Added Dota 2 (570)

        for steam_id in steam_ids:
            url = 'https://vginsights.com/api/v1/game/{}/'.format(steam_id)
            yield scrapy.Request(
                url=url,
                callback=self.parse_main,
                headers=self.headers,
                errback=self.handle_error
            )

    def handle_error(self, failure):
        logging.error(f"Request failed: {failure.value}")
        if hasattr(failure.value, 'response'):
            logging.error(f"Response status: {failure.value.response.status}")
            logging.error(f"Response headers: {failure.value.response.headers}")
            logging.error(f"Response body: {failure.value.response.body}")

    def parse_main(self, response):
        try:
            data = response.json()
        except Exception as e:
            logging.error(f"Failed to parse JSON: {e}")
            logging.error(f"Response body: {response.body}")
            return

        if not data:
            logging.error("Empty response data received")
            return

        self.games_processed += 1
        logging.info(f"Processing game {self.games_processed}: {data.get('name', 'Unknown')} (Steam ID: {data.get('steam_id', 'Unknown')})")

        item = ScraperItem()
        item['steam_id'] = data['steam_id']
        item['developers'] = data['developers']
        item['publishers'] = data['publishers']
        item['first_release_date'] = data['released']
        item['price'] = data['price']
        item['genres'] = data['genres']
        item['tags'] = data['tag_names']
        item['languages'] = data['languages']
        item['short_description'] = data['shortDescription']
        item['title'] = data['name']
        item['slug'] = data['slug']
        
        # Yield the ScraperItem first
        yield item

        # Then make the request for quick stats
        yield scrapy.Request(
            url=f'https://vginsights.com/api/v1/game/{item["slug"]}/quick-stats',
            meta={'item': item},
            callback=self.parse_quick_stats,
            headers=self.headers,
            errback=self.handle_error
        )

    def parse_player_overlap(self, response):
        try:
            data = response.json()
            
            if 'meta' not in data or 'rows' not in data:
                logging.error(f"Unexpected response structure for steam_id {response.meta['steam_id']}")
                return
            
            total_rows = int(data['meta']['selected_rows'])
            current_offset = response.meta['offset']
            steam_id = response.meta['steam_id']
            
            for row in data['rows']:
                item = PlayerOverlapItem()
                item['steam_id'] = steam_id
                item['name'] = row['name']
                item['released'] = row['released']
                item['genres'] = row['genres']
                item['median_playtime'] = row['median_playtime']
                item['owner_overlap'] = row['owner_overlap']
                item['owner_overlap_percentage'] = row['owner_overlap_percentage']
                item['owner_overlap_index'] = row['owner_overlap_index']
                item['mau_overlap'] = row['mau_overlap']
                item['mau_overlap_percentage'] = row['mau_overlap_percentage']
                item['mau_overlap_index'] = row['mau_overlap_index']
                item['wishlist_overlap'] = row['wishlist_overlap']
                item['wishlist_overlap_percentage'] = row['wishlist_overlap_percentage']
                item['wishlist_overlap_index'] = row['wishlist_overlap_index']
                yield item

            next_offset = current_offset + 10
            if next_offset < total_rows:
                next_url = f'https://vginsights.com/api/v1/game/{steam_id}/player-overlap/?limit=10&offset={next_offset}&sortField=owner_overlap_index&sortOrder=-1&gameName='
                
                yield scrapy.Request(
                    url=next_url,
                    meta={'steam_id': steam_id, 'offset': next_offset},
                    callback=self.parse_player_overlap,
                    headers=self.headers,
                    errback=self.handle_error,
                    dont_filter=True
                )

        except Exception as e:
            logging.error(f"Error processing player overlap data for steam_id {steam_id}: {str(e)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")

    def parse_quick_stats(self, response):
        try:
            data = response.json()
            
            # Get the steam data
            steam_data = data.get('steam', {})
            if not steam_data:
                return

            item = QuickStatsItem()
            item['steam_id'] = response.meta['item']['steam_id']
            item['avg_playtime'] = steam_data.get('avg_playtime', 0)
            item['med_playtime'] = steam_data.get('med_playtime', 0)
            item['max_players_24h'] = steam_data.get('max_players_24h', 0)
            item['players_latest'] = steam_data.get('players_latest', 0)
            item['players_latest_time'] = steam_data.get('players_latest_time', '')
            item['daily_active_users'] = steam_data.get('daily_active_users', 0)
            item['monthly_active_users'] = steam_data.get('monthly_active_users', 0)
            item['rating'] = steam_data.get('rating', 0)
            item['revenue_vgi'] = steam_data.get('revenue_vgi', 0)
            item['units_sold_vgi'] = steam_data.get('units_sold_vgi', 0)
            item['wishlist_count'] = steam_data.get('wishlist_count', 0)
            yield item

            # Request player insights data
            yield scrapy.Request(
                url=f'https://vginsights.com/api/v1/game/{response.meta["item"]["slug"]}/regional-info?platform=steam',
                meta={'steam_id': response.meta['item']['steam_id']},
                callback=self.parse_player_insights,
                headers=self.headers,
                errback=self.handle_error
            )

            # Request historical data
            yield scrapy.Request(
                url=f'https://vginsights.com/api/v1/game-history/?slugs={response.meta["item"]["slug"]}&alignToRelease=false&includeEarlyAccess=true',
                meta={'steam_id': response.meta['item']['steam_id']},
                callback=self.parse_historical_data,
                headers=self.headers,
                errback=self.handle_error
            )

        except Exception as e:
            steam_id = response.meta.get('item', {}).get('steam_id', 'unknown')
            logging.error(f"Error processing quick stats for steam_id {steam_id}: {str(e)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")

    def parse_player_insights(self, response):
        try:
            data = response.json()
            
            # Get the steam data
            steam_data = data.get('steam', {})
            if not steam_data:
                return
            
            # Check if we have any valid data
            has_data = False
            for category in ['countries', 'regions', 'playtime', 'games', 'wishlists']:
                if steam_data.get(category) and isinstance(steam_data[category], dict) and 'labels' in steam_data[category] and 'data' in steam_data[category]:
                    if len(steam_data[category]['labels']) > 0 and len(steam_data[category]['data']) > 0:
                        has_data = True
                        break
            
            if not has_data:
                return

            item = PlayerInsightsItem()
            item['steam_id'] = response.meta['steam_id']
            item['countries'] = steam_data.get('countries', {})
            item['regions'] = steam_data.get('regions', {})
            item['playtime'] = steam_data.get('playtime', {})
            item['games'] = steam_data.get('games', {})
            item['wishlists'] = steam_data.get('wishlists', {})
            yield item

        except Exception as e:
            steam_id = response.meta.get('steam_id', 'unknown')
            logging.error(f"Error processing player insights for steam_id {steam_id}: {str(e)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")

    def parse_historical_data(self, response):
        try:
            json_data = response.json()
            
            if not json_data:
                logging.error("Empty response data received")
                return
                
            # The response is a list, get the first item's performance data
            data = json_data[0]['performance']['steam']
            
            item = HistoricalDataItem()
            item['steam_id'] = response.meta['steam_id']
            
            # List of metrics to extract
            metrics = [
                'members', 'wishlist_count', 'players_max', 'players_avg',
                'units', 'units_increase', 'revenue_sum', 'revenue_increase',
                'reviews', 'rating', 'daily_active_users', 'monthly_active_users'
            ]
            
            # Extract each metric if it exists
            for metric in metrics:
                if metric in data:
                    if isinstance(data[metric], dict):
                        if 'firstDate' in data[metric] and 'values' in data[metric]:
                            item[metric] = data[metric]
            
            # Handle price data separately since it has a different structure
            if 'price' in data:
                item['price'] = data['price']
                
            yield item

        except Exception as e:
            steam_id = response.meta.get('steam_id', 'unknown')
            logging.error(f"Error processing historical data for steam_id {steam_id}: {str(e)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
    
    # def parse_save_file(self, response):
    #     file_prefix = response.meta['prefix']
    #     steam_id = response.meta['steam_id']
    #     print(steam_id)
    #     try:
    #         with open(f'excel_files/{file_prefix}/{steam_id}.xlsx', 'wb') as f:
    #             f.write(response.body)
    #     except Exception as e:
    #         logging.error(f"Failed to save file: {e}")
