"""Stubs for tmdbapis simple objects (non-reload, non-pagination).

FindResults has explicitly typed result lists so that subscripting them
(e.g. results.tv_results[0].id) narrows correctly to the specific TMDb object
type rather than the 49-member _parse() union.
"""

from typing import Any

from tmdbapis.objs.base import TMDbObj
from tmdbapis.objs.reload import Episode, Movie, Person, Season, TVShow

class FindResults(TMDbObj):
    movie_results: list[Movie]
    person_results: list[Person]
    tv_episode_results: list[Episode]
    tv_results: list[TVShow]
    tv_season_results: list[Season]
    def __getattr__(self, name: str) -> Any: ...

# All other simple classes: typed minimally; __getattr__ covers the rest.
class AlternativeName(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class AlternativeTitle(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class Certification(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class Country(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class CountryCertifications(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class CountryWatchProviders(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class Department(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class Genre(TMDbObj):
    id: int
    name: Any
    def __getattr__(self, name: str) -> Any: ...

class Group(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class Language(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class ReleaseDate(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class Timezones(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class TMDbList(TMDbObj):
    name: Any
    def get_results(self, amount: int | None = ...) -> list[Any]: ...
    def __len__(self) -> int: ...
    def __getattr__(self, name: str) -> Any: ...

class Trailer(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class Translation(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class User(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class Video(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...

class WatchProvider(TMDbObj):
    def __getattr__(self, name: str) -> Any: ...
