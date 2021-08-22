import pandas as pd
import rating_api.tournaments as rating_tournaments_api

def get_tournaments():
    """Функция, получающая датафрейм со всеми турнирами.
    На данный момент сожержит только турниры сайта рейтинга."""
    rating_tournaments = rating_tournaments_api.get_all_tournaments()
    return rating_tournaments

def save_tournaments(tournaments, path = "tournaments.pkl.bz2", compression="infer"):
    """Функция, сохраняющая датафрейм со всеми турнирами в файл."""
    tournaments.to_pickle(path, compression=compression)

