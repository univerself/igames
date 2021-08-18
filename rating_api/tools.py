# На основе на одноимённого модуля Егора Игнатенкова
# Источник: https://github.com/eignatenkov/chgk-rating

import requests
import json

base_url = "https://rating.chgk.info/api/"

def api_call(url):
    response = requests.get(url)
    return json.loads(response.content.decode("UTF-8"))