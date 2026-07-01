"""Stubs for tmdbapis reload objects.

Key typed attributes are declared explicitly so pyright can narrow them
without the 49-member union explosion that comes from _parse()'s inferred
return type.  Everything else falls through __getattr__ -> Any.

Class ordering matters: Movie and TVShow are declared before Credit because
Credit references both.
"""

from __future__ import annotations

from typing import Any, Optional, Union

from tmdbapis.objs.base import TMDbObj
from tmdbapis.objs.mixin import Favorite, Rate, Watchlist
from tmdbapis.objs.pagination import (
    MovieLists,
    MovieRecommendations,
    MovieReviews,
    RecommendedMovies,
    RecommendedTVShows,
    SimilarMovies,
    SimilarTVShows,
    TaggedImages,
    TMDbPagination,
)

class TMDbReload(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class Account(TMDbReload):
    def __getattr__(self, name: str) -> Any: ...

# ---------------------------------------------------------------------------
# Movie and TVShow declared early so Credit can reference them.
# ---------------------------------------------------------------------------

class Movie(TMDbReload, Favorite, Rate, Watchlist):
    id: int
    title: Any
    imdb_id: Any
    tvdb_id: Any
    release_dates: Any
    def __getattr__(self, name: str) -> Any: ...

class TVShow(TMDbReload, Favorite, Rate, Watchlist):
    id: int
    title: Any
    imdb_id: Any
    tvdb_id: Any
    def __getattr__(self, name: str) -> Any: ...

# ---------------------------------------------------------------------------
# Credit references Movie and TVShow above.
# ---------------------------------------------------------------------------

class Credit(TMDbReload):
    id: Any
    movie: Movie
    tv_show: TVShow
    department: str
    name: Any
    media_type: Any
    def __getattr__(self, name: str) -> Any: ...

# ---------------------------------------------------------------------------
# Remaining classes in alphabetical order.
# ---------------------------------------------------------------------------

class Collection(TMDbReload):
    id: int
    name: Any
    movies: TMDbPagination
    def __getattr__(self, name: str) -> Any: ...

class Company(TMDbReload):
    id: int
    name: Any
    movies: TMDbPagination
    tv_shows: TMDbPagination
    def __getattr__(self, name: str) -> Any: ...

class Configuration(TMDbReload):
    def __getattr__(self, name: str) -> Any: ...

class Episode(TMDbReload, Rate):
    id: int
    tv_id: int
    season_number: int
    episode_number: int
    def __getattr__(self, name: str) -> Any: ...

class EpisodeGroup(TMDbReload):
    def __getattr__(self, name: str) -> Any: ...

class Keyword(TMDbReload):
    id: int
    name: Any
    movies: TMDbPagination
    tv_shows: TMDbPagination
    def __getattr__(self, name: str) -> Any: ...

class Network(TMDbReload):
    id: int
    name: Any
    tv_shows: TMDbPagination
    def __getattr__(self, name: str) -> Any: ...

class Person(TMDbReload):
    id: int
    name: Any
    movie_cast: list[Credit]
    movie_crew: list[Credit]
    tv_cast: list[Credit]
    tv_crew: list[Credit]
    def __getattr__(self, name: str) -> Any: ...

class Review(TMDbReload):
    def __getattr__(self, name: str) -> Any: ...

class Season(TMDbReload):
    id: int
    def __getattr__(self, name: str) -> Any: ...
