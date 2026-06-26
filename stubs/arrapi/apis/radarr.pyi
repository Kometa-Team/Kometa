from typing import Any, List, Optional, Tuple, Union

from arrapi.apis.base import BaseAPI
from arrapi.objs.reload import Movie, QualityProfile, Tag
from arrapi.objs.simple import RootFolder

class RadarrAPI(BaseAPI):
    def __init__(self, url: str, apikey: str, **kwargs: Any) -> None: ...
    def _validate_add_options(
        self,
        root_folder: Any,
        quality_profile: Any,
        monitor: bool = ...,
        search: bool = ...,
        minimum_availability: str = ...,
        tags: Optional[List[Any]] = ...,
    ) -> Any: ...
    def respect_list_exclusions_when_adding(self) -> bool: ...
    def get_movie(
        self,
        movie_id: Optional[int] = ...,
        tmdb_id: Optional[int] = ...,
        imdb_id: Optional[str] = ...,
    ) -> Movie: ...
    def all_movies(self) -> List[Movie]: ...
    def add_multiple_movies(
        self,
        ids: List[Union[int, str, Movie, Tuple[Union[int, str, Movie], str]]],
        root_folder: Union[str, int, RootFolder],
        quality_profile: Union[str, int, QualityProfile],
        monitor: bool = ...,
        search: bool = ...,
        minimum_availability: str = ...,
        tags: Optional[List[Union[str, int, Tag]]] = ...,
        per_request: Optional[int] = ...,
    ) -> Tuple[List[Movie], List[Movie], List[Union[int, str, Movie]], List[int]]: ...
    def edit_multiple_movies(
        self,
        ids: List[Union[int, str, Movie]],
        **kwargs: Any,
    ) -> Tuple[List[Movie], List[Movie]]: ...
    def delete_multiple_movies(
        self,
        ids: List[Union[int, str, Movie]],
        **kwargs: Any,
    ) -> None: ...
