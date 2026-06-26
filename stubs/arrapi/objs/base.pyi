"""Stub for arrapi.objs.base.

The critical fix: _parse() is declared as returning Any.  arrapi uses the
identical pattern as tmdbapis — a BaseObj._parse() with no return annotation
whose inferred union type explodes across every attribute assignment.
"""

from abc import ABC
from typing import Any, Optional, Union

class BaseObj(ABC):
    def _parse(
        self,
        data: Any = ...,
        attrs: Optional[Union[str, list[Any]]] = ...,
        value_type: str = ...,
        default_is_none: bool = ...,
        is_list: bool = ...,
        is_dict: bool = ...,
        extend: bool = ...,
        key: Any = ...,
    ) -> Any: ...
    def __getattr__(self, name: str) -> Any: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
