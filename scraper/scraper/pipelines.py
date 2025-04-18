# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from itemadapter import ItemAdapter
from .items import ScraperItem, QuickStatsItem, PlayerInsightsItem, HistoricalDataItem, PlayerOverlapItem
import logging


class JsonWriterPipeline:
    def __init__(self):
        self.games_data = {}
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if isinstance(item, ScraperItem):
            steam_id = str(adapter.get('steam_id'))
            if steam_id not in self.games_data:
                self.games_data[steam_id] = {}
            self.games_data[steam_id].update(adapter.asdict())
            
        elif isinstance(item, QuickStatsItem):
            steam_id = str(adapter.get('steam_id'))
            if steam_id not in self.games_data:
                self.games_data[steam_id] = {}
            self.games_data[steam_id].update(adapter.asdict())
        
        return item
    
    def close_spider(self, spider):
        os.makedirs('json_files', exist_ok=True)
        with open('json_files/games_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.games_data, f, indent=2, ensure_ascii=False)

class ScraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if isinstance(item, PlayerOverlapItem):
            self.save_player_overlap_to_excel(adapter)
        elif isinstance(item, ScraperItem):
            pass
        elif isinstance(item, QuickStatsItem):
            pass
        elif isinstance(item, PlayerInsightsItem):
            self.save_player_insights_to_excel(adapter, adapter.get('steam_id'))
        elif isinstance(item, HistoricalDataItem):
            self.save_historical_data_to_excel(adapter, adapter.get('steam_id'))
            
        return item

    def save_player_overlap_to_excel(self, adapter):
        try:
            steam_id = adapter.get('steam_id')
            os.makedirs('excel_files/player_overlap', exist_ok=True)
            excel_file = f'excel_files/player_overlap/{steam_id}.xlsx'
            
            genres = adapter.get('genres', [])
            if isinstance(genres, list):
                genres_str = ', '.join(genres)
            else:
                genres_str = str(genres)
            
            data = {
                'name': [adapter.get('name')],
                'released': [adapter.get('released')],
                'genres': [genres_str],
                'median_playtime': [adapter.get('median_playtime')],
                'owner_overlap': [adapter.get('owner_overlap')],
                'owner_overlap_percentage': [adapter.get('owner_overlap_percentage')],
                'owner_overlap_index': [adapter.get('owner_overlap_index')],
                'mau_overlap': [adapter.get('mau_overlap')],
                'mau_overlap_percentage': [adapter.get('mau_overlap_percentage')],
                'mau_overlap_index': [adapter.get('mau_overlap_index')],
                'wishlist_overlap': [adapter.get('wishlist_overlap')],
                'wishlist_overlap_percentage': [adapter.get('wishlist_overlap_percentage')],
                'wishlist_overlap_index': [adapter.get('wishlist_overlap_index')]
            }
            
            df = pd.DataFrame(data)
            
            if os.path.exists(excel_file):
                existing_df = pd.read_excel(excel_file, sheet_name='Player Overlap')
                df = pd.concat([existing_df, df], ignore_index=True)
                df.to_excel(excel_file, sheet_name='Player Overlap', index=False)
            else:
                df.to_excel(excel_file, sheet_name='Player Overlap', index=False)
                
        except Exception as e:
            logging.error(f"Error saving player overlap data for steam_id {steam_id}: {e}")

    def save_historical_data_to_excel(self, adapter, steam_id):
        try:
            os.makedirs('excel_files/historical_data', exist_ok=True)
            excel_file = f'excel_files/historical_data/{steam_id}.xlsx'
            
            metrics = [
                'members', 'wishlist_count', 'players_max', 'players_avg',
                'units', 'units_increase', 'revenue_sum', 'revenue_increase',
                'reviews', 'rating', 'daily_active_users', 'monthly_active_users'
            ]
            
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                for metric in metrics:
                    try:
                        data = adapter.get(metric)
                        if data and isinstance(data, dict) and 'firstDate' in data and 'values' in data:
                            start_date = datetime.strptime(data['firstDate'], '%Y-%m-%d')
                            dates = [start_date + timedelta(days=i) for i in range(len(data['values']))]
                            df = pd.DataFrame({
                                'Date': dates,
                                'Value': data['values']
                            })
                            df.to_excel(writer, sheet_name=metric.capitalize(), index=False)
                    except Exception as e:
                        logging.error(f"Error processing {metric} for steam_id {steam_id}: {str(e)}")

                try:
                    price_data = adapter.get('price')
                    if price_data and isinstance(price_data, list):
                        df = pd.DataFrame(price_data)
                        df['ts'] = pd.to_datetime(df['ts'])
                        df = df[['ts', 'initial', 'final', 'days', 'day_nr']]
                        df.to_excel(writer, sheet_name='Price', index=False)
                except Exception as e:
                    logging.error(f"Error processing price data for steam_id {steam_id}: {str(e)}")

        except Exception as e:
            logging.error(f"Error saving historical data for steam_id {steam_id}: {str(e)}")

    def save_player_insights_to_excel(self, adapter, steam_id):
        try:
            os.makedirs('excel_files/player_insights', exist_ok=True)
            excel_file = f'excel_files/player_insights/{steam_id}.xlsx'
            
            has_data = False
            for category in ['countries', 'regions', 'playtime', 'games', 'wishlists']:
                data = adapter.get(category)
                if data and isinstance(data, dict) and 'labels' in data and 'data' in data:
                    if len(data['labels']) > 0 and len(data['data']) > 0:
                        has_data = True
                        break
            
            if not has_data:
                return

            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                for category in ['countries', 'regions', 'playtime', 'games', 'wishlists']:
                    data = adapter.get(category)
                    if data and isinstance(data, dict) and 'labels' in data and 'data' in data:
                        if len(data['labels']) > 0 and len(data['data']) > 0:
                            try:
                                df = pd.DataFrame({
                                    'Label': data['labels'],
                                    'Value': data['data']
                                })
                                df.to_excel(writer, sheet_name=category.capitalize(), index=False)
                            except Exception as e:
                                logging.error(f"Error processing {category} for steam_id {steam_id}: {str(e)}")

        except Exception as e:
            logging.error(f"Error saving player insights for steam_id {steam_id}: {str(e)}")























