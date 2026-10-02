"""Top-level re-exports for the arrapi package stub.

Mirrors the runtime __init__.py so that `from arrapi import RadarrAPI` etc.
resolve through the stubs rather than the library source.
"""

from arrapi.apis.radarr import RadarrAPI as RadarrAPI
from arrapi.apis.sonarr import SonarrAPI as SonarrAPI
from arrapi.exceptions import ArrException as ArrException
from arrapi.exceptions import ConnectionFailure as ConnectionFailure
from arrapi.exceptions import Excluded as Excluded
from arrapi.exceptions import Exists as Exists
from arrapi.exceptions import Invalid as Invalid
from arrapi.exceptions import NotFound as NotFound
from arrapi.exceptions import Unauthorized as Unauthorized
from arrapi.objs.reload import LanguageProfile as LanguageProfile
from arrapi.objs.reload import Movie as Movie
from arrapi.objs.reload import QualityProfile as QualityProfile
from arrapi.objs.reload import Series as Series
from arrapi.objs.reload import SystemStatus as SystemStatus
from arrapi.objs.reload import Tag as Tag
from arrapi.objs.simple import MetadataProfile as MetadataProfile
from arrapi.objs.simple import RemotePathMapping as RemotePathMapping
from arrapi.objs.simple import RootFolder as RootFolder
from arrapi.objs.simple import Season as Season
from arrapi.objs.simple import UnmappedFolder as UnmappedFolder

__version__: str
