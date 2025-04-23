import requests
import json
import os
import sys
from typing import Generator, List, Dict, Any

# Add the project root to Python path when running as script
if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from config import SITE_TOKEN
else:
    from config import SITE_TOKEN

BASE_URL = 'https://vginsights.com/api/v1/games'
PAGE_SIZE = 20
MAX_GAMES = 50000


def get_top_steam_games(limit=5):
    results = []
    base_url = 'https://steamspy.com/api.php?request=all&page='
    for i in range(1, limit + 1):
        page_url = base_url + str(i)
        response = requests.get(page_url)
        if response.status_code == 200:
            json_response = json.loads(response.text)
            for appid in json_response:
                results.append(sappid)
        else:
            print("There was an error in getting data in page {}".format(i))
    return results


def get_steam_ids_from_vginsights() -> Generator[List[Dict[str, Any]], None, None]:
    """
    Get Steam games from VGInsights API.
    
    Yields:
        List[Dict[str, Any]]: A list of 20 game dictionaries containing steam_id and other game data
    """
    offset = 0
    total_games = None
    games_processed = 0
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Authorization': SITE_TOKEN,
    }
    
    while True:
        # Construct the URL with query parameters
        params = {
            'limit': 20,
            'offset': offset,
            'sortOrder': 1,
            'isGamePageRequest': 'true',
            'selectedPlatforms': 'steam'
        }
        
        response = requests.get('https://vginsights.com/api/v1/games', params=params, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching data from VGInsights: {response.status_code}")
            break
            
        data = response.json()
        
        # Get total number of games on first request
        if total_games is None:
            total_games = int(data['meta']['selected_rows'])
        
        # Yield current page of games (20 games)
        yield data['rows']
        
        # Update counters
        games_processed += len(data['rows'])
        print(f"Processed {games_processed} games out of {min(total_games, MAX_GAMES)}")
        
        # Update offset for next page
        offset += 20
        
        # Check if we've reached the limit or end of data
        if offset >= total_games or games_processed >= MAX_GAMES:
            print(f"Finished processing {games_processed} games")
            break


if __name__ == '__main__':
    a = get_steam_ids_from_vginsights()
    for i in a:
        print(i)