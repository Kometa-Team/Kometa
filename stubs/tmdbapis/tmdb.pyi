"""Stub for TMDbAPIs — the top-level client class.

Methods are typed with their proper return types.  __getattr__ covers any
method not listed here (rare in practice; Kometa only uses a small subset).
"""

from typing import Any, Dict, List, Optional, Union

from tmdbapis.exceptions import Invalid, NotFound, TMDbException
from tmdbapis.objs.pagination import (
    DiscoverMovies,
    DiscoverTVShows,
    NowPlayingMovies,
    PopularMovies,
    PopularPeople,
    PopularTVShows,
    SearchPeople,
    TopRatedMovies,
    TopRatedTVShows,
    TrendingAll,
    TVAiringToday,
    TVOnAir,
    UpcomingMovies,
)
from tmdbapis.objs.reload import Collection, Company, Episode, Keyword, Movie, Network, Person, Season, TVShow
from tmdbapis.objs.simple import FindResults, Genre, Language, TMDbList, WatchProvider

discover_movie_sort_options: list[str]
discover_tv_sort_options: list[str]

class TMDbAPIs:
    def __init__(
        self,
        apikey: str,
        language: str = ...,
        session: Any = ...,
    ) -> None: ...

    # ------------------------------------------------------------------
    # Find / lookup
    # ------------------------------------------------------------------
    def find_by_id(
        self,
        imdb_id: Optional[str] = ...,
        freebase_mid: Optional[str] = ...,
        freebase_id: Optional[str] = ...,
        tvdb_id: Optional[str] = ...,
        tvrage_id: Optional[str] = ...,
        facebook_id: Optional[str] = ...,
        twitter_id: Optional[str] = ...,
        instagram_id: Optional[str] = ...,
    ) -> FindResults: ...

    # ------------------------------------------------------------------
    # Single-object retrieval
    # ------------------------------------------------------------------
    def collection(
        self,
        collection_id: int,
        load: bool = ...,
        partial: Optional[Union[bool, str]] = ...,
    ) -> Collection: ...
    def company(
        self,
        company_id: int,
        load: bool = ...,
        partial: Optional[Union[bool, str]] = ...,
    ) -> Company: ...
    def keyword(self, keyword_id: int, load: bool = ...) -> Keyword: ...
    def list(self, list_id: int, load: bool = ...) -> TMDbList: ...
    def movie(
        self,
        movie_id: int,
        load: bool = ...,
        partial: Optional[Union[bool, str]] = ...,
    ) -> Movie: ...
    def network(
        self,
        network_id: int,
        load: bool = ...,
        partial: Optional[Union[bool, str]] = ...,
    ) -> Network: ...
    def person(
        self,
        person_id: int,
        load: bool = ...,
        partial: Optional[Union[bool, str]] = ...,
    ) -> Person: ...
    def tv_show(
        self,
        tv_id: int,
        load: bool = ...,
        partial: Optional[Union[bool, str]] = ...,
    ) -> TVShow: ...
    def tv_season(
        self,
        tv_id: int,
        season_number: int,
        load: bool = ...,
        partial: Optional[Union[bool, str]] = ...,
    ) -> Season: ...

    # ------------------------------------------------------------------
    # Discover / trending / charts
    # ------------------------------------------------------------------
    def discover_movies(self, **kwargs: Any) -> DiscoverMovies: ...
    def discover_tv_shows(self, **kwargs: Any) -> DiscoverTVShows: ...
    def now_playing_movies(self, region: Any = ...) -> NowPlayingMovies: ...
    def popular_movies(self, region: Any = ...) -> PopularMovies: ...
    def popular_people(self) -> PopularPeople: ...
    def popular_tv(self) -> PopularTVShows: ...
    def top_rated_movies(self, region: Any = ...) -> TopRatedMovies: ...
    def top_rated_tv(self) -> TopRatedTVShows: ...
    def trending(self, media_type: str, time_window: str) -> TrendingAll: ...
    def tv_airing_today(self) -> TVAiringToday: ...
    def tv_on_the_air(self) -> TVOnAir: ...
    def upcoming_movies(self, region: Any = ...) -> UpcomingMovies: ...

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def people_search(self, query: str, **kwargs: Any) -> SearchPeople: ...

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------
    def movie_certifications(self, reload: bool = ...) -> Dict[str, Any]: ...
    def movie_genres(self, reload: bool = ...) -> List[Genre]: ...
    def tv_genres(self, reload: bool = ...) -> List[Genre]: ...
    def __getattr__(self, name: str) -> Any: ...
