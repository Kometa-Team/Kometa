from typing import Any, List, Optional, Tuple, Union

from arrapi.apis.base import BaseAPI
from arrapi.objs.reload import LanguageProfile, QualityProfile, Series, Tag
from arrapi.objs.simple import RootFolder

class SonarrAPI(BaseAPI):
    _raw: Any  # internal raw API object; has attributes like .v3, .v4, .new_codebase
    def __init__(self, url: str, apikey: str, **kwargs: Any) -> None: ...
    def _validate_add_options(
        self,
        root_folder: Any,
        quality_profile: Any,
        language_profile: Optional[Any] = ...,
        monitor: str = ...,
        season_folder: bool = ...,
        search: bool = ...,
        unmet_search: bool = ...,
        series_type: str = ...,
        tags: Optional[List[Any]] = ...,
    ) -> Any: ...
    def respect_list_exclusions_when_adding(self) -> bool: ...
    def get_series(
        self,
        series_id: Optional[int] = ...,
        tvdb_id: Optional[int] = ...,
    ) -> Series: ...
    def all_series(self) -> List[Series]: ...
    def add_multiple_series(
        self,
        ids: List[Union[Series, int, Tuple[Union[Series, int], str]]],
        root_folder: Union[str, int, RootFolder],
        quality_profile: Union[str, int, QualityProfile],
        language_profile: Optional[Union[str, int, LanguageProfile]] = ...,
        monitor: str = ...,
        season_folder: bool = ...,
        search: bool = ...,
        unmet_search: bool = ...,
        series_type: str = ...,
        tags: Optional[List[Union[str, int, Tag]]] = ...,
        per_request: Optional[int] = ...,
    ) -> Tuple[List[Series], List[Series], List[Union[int, Series]], List[int]]: ...
    def edit_multiple_series(
        self,
        ids: List[Union[int, Series]],
        **kwargs: Any,
    ) -> Tuple[List[Series], List[Series]]: ...
    def delete_multiple_series(
        self,
        ids: List[Union[int, Series]],
        **kwargs: Any,
    ) -> None: ...
