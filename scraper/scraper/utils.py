import requests
import json

base_url = 'https://steamspy.com/api.php?request=all&page='


def get_top_steam_games(limit=5):
    results = []
    for i in range(1, limit + 1):
        page_url = base_url + str(i)
        response = requests.get(page_url)
        if response.status_code == 200:
            json_response = json.loads(response.text)
            for appid in json_response:
                results.append(appid)
        else:
            print("There was an error in getting data in page {}".format(i))
    return results
