# На основе на одноимённого модуля Егора Игнатенкова
# Источник: https://github.com/eignatenkov/chgk-rating

import requests
import json

def api_call(url, base_url = "https://rating.chgk.info/api/"):
    response = requests.get(base_url + url)
    return json.loads(response.content.decode("UTF-8"))