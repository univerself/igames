# На основе на одноимённого модуля Егора Игнатенкова
# Источник: https://github.com/eignatenkov/chgk-rating

import math
import datetime
from dateutil.parser import parse as date_parse

from rating_api.tools import api_call, base_url

def get_tournaments(page=None):
    url = base_url + "tournaments.json"
    if page:
        url += "/?page={}".format(page)
    return api_call(url)


def get_all_tournaments():
    all_tournaments = []
    page = 1
    while True:
        next_page = get_tournaments(page=page)
        if not next_page:
            break
        all_tournaments += next_page
        page += 1
    return all_tournaments


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
