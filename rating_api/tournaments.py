# На основе на одноимённого модуля Егора Игнатенкова
# Источник: https://github.com/eignatenkov/chgk-rating

import math
import datetime
from dateutil.parser import parse as date_parse
import pandas as pd
from itertools import count

from rating_api.tools import api_call

def get_tournaments(page=None):
    url = "tournaments.json"
    if page:
        url += "/?page={}".format(page)
    parsed_json = api_call(url)
    return pd.json_normalize(parsed_json["items"])

def next_tournaments_df():
    """Функция-генератор, получающая датафрейм из следующей по порядку страницы сайта рейтинга."""
    for page in count(1):
        page_df = get_tournaments(page=page)
        if not page_df.size:
            return
        yield page_df

# Функция получает датафрейм со всеми .
def get_all_tournaments():
    """Функция, получающая датафрейм со всеми турнирами сайта рейтинга."""
    return pd.concat([df for df in next_tournaments_df()])

# Функция получает данные по конкретному турниру.
def get_tournament_info(tournament_id):
    return pd.json_normalize(
        api_call("tournaments/{}/list".format(tournament_id))
    )

def get_tournament_results(tournament_id, recaps=False, rating=False, mask=False):
    url = f"{base_url}/tournaments/{tournament_id}/results.json" \
          f"?includeTeamMembers={int(recaps)}&includeRatingB={int(rating)}&" \
          f"includeMasksAndControversials={int(mask)}"
    return api_call(url)


def get_tournaments_for_release(release_date: datetime.datetime):
    result = []
    tournaments = get_all_tournaments()
    for t in tournaments:
        try:
            t_end = date_parse(t["date_end"])
        except ValueError:
            continue
        if release_date > t_end >= release_date - datetime.timedelta(days=7) and t['type_name'] in \
                {'Обычный', 'Синхрон'}:
            result.append(t)
    return result
