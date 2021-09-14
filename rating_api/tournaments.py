# На основе на одноимённого модуля Егора Игнатенкова
# Источник: https://github.com/eignatenkov/chgk-rating

import math
import datetime
from dateutil.parser import parse as date_parse
import pandas as pd
from itertools import count

from rating_api.tools import api_call

def to_tournament_df(parsed_json, long_name = None, tournament_in_rating = None):
    df = pd.json_normalize(parsed_json)
    if df.empty:
        return df
    df.fillna({"tour_count": 0, 
               "tour_questions": 0, 
               "tour_ques_per_tour": 0,
               "questions_total": 0,
               "main_payment_value": 0,
               "discounted_payment_value": 0},
              inplace = True)
    df = df.assign(long_name=df[long_name if long_name else "long_name"],
                   date_start=pd.to_datetime(df["date_start"], errors='coerce'),
                   date_end=pd.to_datetime(df["date_end"], errors='coerce'),
                   tournament_in_rating=tournament_in_rating,
                   archive=(df["archive"]  == '1'),
                   date_archived_at=pd.to_datetime(df["date_archived_at"], errors='coerce'))
        
    df = df.astype({
        "idtournament": "int32", 
        "name": "string", 
        "long_name": "string", 
        "town": "string",
        "type_name": "category",
        "tour_count": "int32", 
        "tour_questions": "int32", 
        "tour_ques_per_tour": "string", 
        "questions_total": "int32", 
        "main_payment_value": "float64", 
        "main_payment_currency": "string",
        "discounted_payment_value": "float64", 
        "discounted_payment_currency": "string",
        "discounted_payment_reason": "string", 
        "tournament_in_rating": "boolean", 
        "date_requests_allowed_to": "datetime64[ns]", 
        "comment": "string", 
        "site_url": "string", 
        "archive": "boolean"
    })
    return df

def get_tournaments(page=None):
    url = "tournaments.json"
    if page:
        url += "/?page={}".format(page)
    parsed_json = api_call(url)
    df = pd.json_normalize(parsed_json["items"])
    if df.empty:
        return df
    
    df = df.assign(long_name=df["name"],
                   town=None,
                   date_start=pd.to_datetime(df["date_start"], errors='coerce'),
                   date_end=pd.to_datetime(df["date_end"], errors='coerce'),
                   tour_count=0,
                   tour_questions=0,
                   tour_ques_per_tour=0,
                   questions_total=0,
                   main_payment_value=0.0,
                   main_payment_currency=None,
                   discounted_payment_value=0.0,
                   discounted_payment_currency=None,
                   discounted_payment_reason=None,
                   tournament_in_rating=None,
                   date_requests_allowed_to=None,
                   comment=None,
                   site_url=None,
                   archive=(df["archive"]  == '1'),
                   date_archived_at=pd.to_datetime(df["date_archived_at"], errors='coerce'),
                   db_tags=None)
    df = df.astype({
        "idtournament": "int32", 
        "name": "string", 
        "long_name": "string", 
        "town": "string",
        "type_name": "category",
        "tour_count": "int32", 
        "tour_questions": "int32", 
        "tour_ques_per_tour": "string", 
        "questions_total": "int32", 
        "main_payment_value": "float64", 
        "main_payment_currency": "string",
        "discounted_payment_value": "float64", 
        "discounted_payment_currency": "string",
        "discounted_payment_reason": "string", 
        "tournament_in_rating": "boolean", 
        "date_requests_allowed_to": "datetime64[ns]", 
        "comment": "string", 
        "site_url": "string", 
        "archive": "boolean"
    })
    df.type_name = df.type_name.cat.set_categories(["Обычный", "Синхрон"])
    df.index = df.idtournament
    return df

def next_tournaments_df():
    """Функция-генератор, получающая датафрейм из следующей по порядку страницы сайта рейтинга."""
    for page in count(1):
        page_df = get_tournaments(page=page)
        if page_df.empty:
            return
        yield page_df

def get_all_tournaments():
    """Функция, получающая датафрейм со всеми турнирами сайта рейтинга."""
    return pd.concat([df for df in next_tournaments_df()])

def get_tournament_info(tournament_id):
    """Функция, получающая данные по конкретному турниру."""
    res = api_call(f"tournaments/{tournament_id}")
    df = to_tournament_df(res, 
                          tournament_in_rating = lambda x: x['tournament_in_rating'] == '1')
    return df

def update_tournament_info(tournaments, tournament_id):
    old_rows_index = tournaments[tournaments["idtournament"] == tournament_id].index
    if not old_rows_index.empty:
        tournaments.drop(old_rows_index, inplace = True)
    tournaments = tournaments.append(get_tournament_info(tournament_id), ignore_index=True)
    return tournaments

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
