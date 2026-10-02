from typing import Any

class Favorite:
    def __getattr__(self, name: str) -> Any: ...

class Rate:
    def __getattr__(self, name: str) -> Any: ...

class Watchlist:
    def __getattr__(self, name: str) -> Any: ...
