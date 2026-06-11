from __future__ import annotations

import os, types, requests, mimetypes, base64, tempfile
from urllib.parse import urlparse
from modules import util
from modules.library import Library
from modules.util import Failed
from plexapi.video import Movie

import jellyfin
from jellyfin.items import Item
from jellyfin.generated import (
    BaseItemDto, 
    BaseItemKind, 
    CollectionApi, 
    CollectionType,
    LibraryApi,
    ItemFields,
    ImageType,
    MetadataField
)

logger = util.logger

class Jellyfin(Library):
    def __init__(self, config, params):
        """ Initializes Jellyfin Object 
        
        Args:
            config (modules.config.ConfigFile): Config object
            params (dict): Dictionary of Jellyfin parameters
        """
        # TODO: https://github.com/Kometa-Team/Kometa/pull/2788
        params["plex"] = {}
        params["plex"]["optimize"] = None
        params["plex"]["clean_bundles"] = None
        params["plex"]["empty_trash"] = None
        
        super().__init__(config, params)

        # TODO: https://github.com/Kometa-Team/Kometa/issues/2791
        self.config.Cache.query_image_map = types.MethodType(
            lambda self, rating_key, table_name: (None, None, None),
            self.config.Cache
        )
        
        self.config.Cache.update_image_map = types.MethodType(
            lambda self, rating_key, table_name, location, compare, overlay=None: None,
            self.config.Cache
        )

        self.jellyfin = params["jellyfin"]
        self.url = self.jellyfin["url"]
        self.session = self.config.Requests.session
        
        # not used by jellyfin
        self.clean_bundles = False
        self.empty_trash = False
        self.optimize = False
        
        # the builder make reference to Plex directly so we set it here
        self.Plex = PlexWrapper(self)
        
        # jellyfin does not have a language setting per library
        self.language = "en"

        if self.jellyfin["verify_ssl"] is False and self.config.Requests.global_ssl is True:
            logger.debug("Overriding verify_ssl to False for Jellyfin connection")
            self.session = self.config.Requests.create_session(verify_ssl=False)
        if self.jellyfin["verify_ssl"] is True and self.config.Requests.global_ssl is False:
            logger.debug("Overriding verify_ssl to True for Jellyfin connection")
            self.session = self.config.Requests.create_session()

        self.token = self.jellyfin["token"]
        self.timeout = self.jellyfin["timeout"]
        
        self.api = jellyfin.api(self.url, self.token)
        
        # we register a client to identify ourselves to the server
        self.api.register_client(client_name="Kometa")

        # some api methods require a user context, so we store the user here
        self.api.user = self.jellyfin["user"]

        # we also wrap the server object to match Plex server interface
        self.PlexServer = ServerWrapper(self.api.system)

        logger.info(self.url)
        logger.secret(self.token)
        try:
            self._server_version = self.api.system.info.version
            self._server_name = self.api.system.info.server_name

            logger.info(f"Connected to server {self._server_name} version {self._server_version}")
        except Exception as e:
            logger.info(f"Jellyfin Error: Jellyfin connection attempt failed")
            logger.stacktrace()
            raise Failed(f"Jellyfin Error: {e}")
        
        library_name = params["name"]
        libraries = list(self.api.items.search.only_library().add('name_starts_with', library_name).all)
        exact_libraries = [
            library for library in libraries
            if library.name and library.name.casefold() == library_name.casefold()
        ]
        if exact_libraries:
            libraries = exact_libraries
        
        if len(libraries) > 1:
            names = [f"'{item.name}' ({item.id.hex})" for item in libraries]
            raise Failed(f"Jellyfin Library '{library_name}' is not unique. Options: {names}")

        if len(libraries) < 1:
            raise Failed(f"Jellyfin Library '{library_name}' not found.")

        item = libraries[0]
        self.Jellyfin = item
        self.type = item.collection_type.value
        
        if item.collection_type == CollectionType.MOVIES:
            self.type = "Movie"

        self.is_movie = self.type == "Movie"
        self.is_show = self.type == "TVShow"
        self.is_music = self.type == "Music"
        self.is_playlist = self.type == "Playlist"
        self.is_other = self.type == "Boxset"

        self._all_items = []

    def notify(self, text: str, collection: str | None = None, critical: bool = True) -> None:
        """ Sends a notification to the server.
        
        Args:
            text (str): The text of the notification.
            collection (str | None): The collection the notification is for. Defaults to None.
            critical (bool): Whether the notification is critical. Defaults to True.
        """
        self.config.notify(text, server=self._server_name, library=self.name, collection=collection, critical=critical)

    def get_all(self, builder_level: str | None = None, load: bool = False) -> list[ItemMovieWrapper]:
        """ Returns all items in the library.
        
        Args:
            builder_level (str | None): The type of items to return. Defaults to None.
            load (bool): Whether to force a reload of all items. Defaults to False.
            
        Returns:
            list[ItemMovieWrapper]: A list of all items in the library.
        """
         # cache all items for movie libraries
        if load and builder_level in [None, "movie"]:
            self._all_items = []
        if self._all_items and builder_level in [None, "movie"]:
            return self._all_items
        builder_level = self.type
        
        logger.info(f"Loading All {builder_level.capitalize()} from Library: {self.name}")
        
        search = self.api.items.search
        search.include_item_types = [BaseItemKind.MOVIE]
        search.fields = [ItemFields.PROVIDERIDS, ItemFields.PATH]
        search.recursive()
        result = []

        for item in search.all:
            result.append(ItemMovieWrapper(item))

        logger.info(f"Loaded {len(result)} {builder_level.capitalize()}")

        if builder_level in [None, "movie"]:
            self._all_items = result
        return result

    def get_all_collections(self, label: str | None = None) -> list[ItemMovieWrapper]:
        """ Returns all collections in the library. 
        
        Args:
            label (str | None): The label to filter collections by. Defaults to None.
        
        Returns:
            list[ItemMovieWrapper]: A list of all collections in the library.
        """
        search = self.api.items.search
        search.include_item_types = [BaseItemKind.BOXSET]
        
        result = []
        for item in search.all:
            result.append(ItemMovieWrapper(item))
        return result

    def get_collection(
            self, 
            data: str, 
            force_search: bool = False, 
            debug: bool = True
        ) -> ItemMovieWrapper:
        """ Returns a collection by name.
        
        Args:
            data (str): The name of the collection.
            force_search (bool): Whether to force a search for the collection. Defaults to False.
            debug (bool): Whether to print debug information. Defaults to True.
            
        Returns:
            ItemMovieWrapper: The collection object.
        """
        search = self.api.items.search
        search.include_item_types = [BaseItemKind.BOXSET]
        collections = search.recursive().all
        for collection in collections:
            if collection.name == data:
                return ItemMovieWrapper(collection)

        item = Item(BaseItemDto())
        item.name = data
        return ItemMovieWrapper(item)

    def split(self, text):
        attribute, modifier = os.path.splitext(str(text).lower())
        final = f"{attribute}{modifier}"
        return attribute, modifier, final

    @staticmethod
    def _jellyfin_id(value):
        """Return a Jellyfin-safe item id string."""
        if value is None:
            return None
        return getattr(value, "hex", None) or str(value).replace("-", "")

    @staticmethod
    def _chunks(values, size=50):
        """Yield small batches so collection item URLs do not exceed proxy/server limits."""
        for index in range(0, len(values), size):
            yield values[index:index + size]

    @staticmethod
    def _metadata_names(raw_values):
        """Normalize Jellyfin metadata values such as tags, genres, and studios."""
        if raw_values is None:
            return []
        if not isinstance(raw_values, list):
            raw_values = [raw_values]

        names = []
        for value in raw_values:
            name = (
                getattr(value, "name", None)
                or getattr(value, "Name", None)
                or getattr(value, "tag", None)
                or str(value)
            )
            name = str(name).strip()
            if name and name.lower() != "none":
                names.append(name)
        return names
    
    def fetch_item(self, item):
        key = item
        if key in self.cached_items:
            return self.cached_items[key][0]
        raise Failed(f"Jellyfin Error: Item {item} not found")

    def search(self, title=None, libtype=None, label=None, sort=None, maxresults=None, **kwargs):
        """Return Jellyfin items for Plex-style library.search calls.

        Kometa overlay cleanup calls library.search(label=..., libtype=...). Plex
        handles that server-side. For Jellyfin we query the current library and
        apply the label/title filters locally.
        """
        search = self.api.items.search.recursive()
        search.parent_id = self.Jellyfin.id

        final_libtype = str(libtype or "").lower()
        if final_libtype in ["collection", "collections", "boxset", "boxsets"]:
            search.include_item_types = [BaseItemKind.BOXSET]
        elif final_libtype in ["show", "series", "tvshow", "tv"] and hasattr(BaseItemKind, "SERIES"):
            search.include_item_types = [BaseItemKind.SERIES]
        elif final_libtype in ["movie", "movies", ""] or self.is_movie:
            search.include_item_types = [BaseItemKind.MOVIE]

        field_names = ["PROVIDERIDS", "PATH", "GENRES", "TAGS", "STUDIOS"]
        fields = [getattr(ItemFields, name) for name in field_names if hasattr(ItemFields, name)]
        if fields:
            search.fields = fields

        results = [ItemMovieWrapper(item) for item in search.all]

        if title:
            wanted_title = str(title).casefold()
            results = [item for item in results if wanted_title in item.title.casefold()]

        if label:
            labels = label if isinstance(label, (list, tuple, set)) else [label]
            wanted_labels = {str(value).casefold() for value in labels if value is not None}
            results = [
                item for item in results
                if wanted_labels.intersection({tag.casefold() for tag in self._metadata_names(getattr(item.item, "tags", None))})
            ]

        if sort:
            sort_value = str(sort)
            reverse = sort_value.endswith(".desc") or sort_value.endswith(":desc")
            if "title" in sort_value.lower():
                results.sort(key=lambda item: item.title.casefold(), reverse=reverse)
            elif "year" in sort_value.lower() or "release" in sort_value.lower() or "available" in sort_value.lower():
                results.sort(key=lambda item: (item.year, item.title.casefold()), reverse=reverse)

        if maxresults:
            try:
                results = results[:int(maxresults)]
            except (TypeError, ValueError):
                pass

        return results

    def get_collection_items(
            self, 
            collection: str | ItemCollectionWrapper, 
            smart_label_collection: bool = False
        ) -> list[ItemMovieWrapper]:
        """ Returns the items of a collection.
        
        Args:
            collection (str | ItemCollectionWrapper): The name or object of the collection.
            smart_label_collection (bool): Whether the collection is a smart label collection.
            
        Returns:
            list[ItemMovieWrapper]: The items of the collection.
        """
        if smart_label_collection is True:
            warn_msg = "Jellyfin smart label collections are not supported"
            logger.warning(warn_msg)
            
        name = collection if isinstance(collection, str) else collection.title
        item = self.get_collection(name)
        
        if item.ratingKey == 0:
            return []

        search = self.api.items.search.recursive()
        search.include_item_types = [BaseItemKind.MOVIE]
        search.parent_id = item.id
        result = []
        for movie in search.all:
            result.append(ItemMovieWrapper(movie))
        return result

    def get_collection_name_and_items(
            self, 
            collection: str | ItemCollectionWrapper, 
            smart_label_collection: bool = False
        ) -> tuple[str, list[ItemMovieWrapper]]:
        """ Returns the name and items of a collection. 
        
        Args:
            collection (str | ItemCollectionWrapper): The name or object of the collection.
            smart_label_collection (bool): Whether the collection is a smart label collection.
            
        Returns:
            tuple[str, list[ItemMovieWrapper]]: The name and items of the collection.
        """
        if smart_label_collection is True:
            warn_msg = "Jellyfin smart label collections are not supported"
            logger.warning(warn_msg)
            
        name = collection if isinstance(collection, str) else collection.title
        return name, self.get_collection_items(collection, smart_label_collection)

    def alter_collection(
            self, 
            items: list[ItemMovieWrapper], 
            collection: str, 
            smart_label_collection=False, 
            add=True
        ) -> None:
        """ Alters a collection by adding or removing items.
        
        Args:
            items (list[ItemMovieWrapper]): The items to add or remove.
            collection (str): The name of the collection.
            smart_label_collection (bool): Whether the collection is a smart label collection. Defaults to False.
            add (bool): Whether to add or remove the items. Defaults to True.
        """
        if smart_label_collection is True:
            warn_msg = "Jellyfin smart label collections are not supported"
            logger.warning(warn_msg)
        
        item = self.get_collection(collection)
        
        if item.ratingKey == 0:
            item = self.create_collection(item)

        if item.id is None:
            raise Failed(f"Jellyfin Error: Could not create collection {collection}")

        if add:
            self.add_to_collection(items, item)
        else:
            self.remove_from_collection(items, item)
            
    def create_smart_collection(
            self,
            title: str,
            smart_type_key: str | int | None = None,
            smart_url: str | dict | None = None,
            ignore_blank_results: bool = False
        ) -> ItemMovieWrapper | None:
        """Materialize a Kometa smart collection as a normal Jellyfin collection.

        Jellyfin does not support Plex smart collections, but Kometa's default
        dynamic genre files still call create_smart_collection after resolving
        the smart filter. We resolve the Plex-style smart URL with fetchItems()
        and then create/update a regular Jellyfin box set with those items.
        """
        items = self.fetchItems(smart_url)

        if not items:
            message = f"Jellyfin Error: Smart collection '{title}' returned no items"
            if ignore_blank_results:
                logger.warning(message)
                return None
            raise Failed(message)

        logger.info(f"Jellyfin: Creating static collection '{title}' from {len(items)} smart filter items")
        self.alter_collection(items, title, add=True)
        return self.get_collection(title)


    def create_collection(self, item: ItemMovieWrapper) -> ItemMovieWrapper:
        """ Creates a new collection.
        
        Args:
            item (ItemMovieWrapper): The collection to create.
            
        Returns:
            ItemMovieWrapper: The created collection object.
        """
        collection = CollectionApi().create_collection(
            name=item.title,
            parent_id=self.Jellyfin.id
        )

        item.id = collection.id
        return item

    def add_to_collection(self, items: list[ItemMovieWrapper], collection: ItemMovieWrapper) -> None:
        """ Adds items to a collection.
        
        Args:
            items (list[ItemMovieWrapper]): The items to add.
            collection (ItemMovieWrapper): The collection to add the items to.
        """
        collection_id = self._jellyfin_id(collection.id)
        item_ids = [self._jellyfin_id(item.id) for item in items if getattr(item, "id", None)]

        for item_id_batch in self._chunks(item_ids):
            if item_id_batch:
                CollectionApi().add_to_collection(collection_id, item_id_batch)
        
    def remove_from_collection(self, items: list[ItemMovieWrapper], collection: ItemMovieWrapper) -> None:
        """ Removes items from a collection.
        
        Args:
            items (list[ItemMovieWrapper]): The items to remove.
            collection (ItemMovieWrapper): The collection to remove the items from.
        """
        collection_id = self._jellyfin_id(collection.id)
        item_ids = [self._jellyfin_id(item.id) for item in items if getattr(item, "id", None)]

        for item_id_batch in self._chunks(item_ids):
            if item_id_batch:
                CollectionApi().remove_from_collection(collection_id, item_id_batch)

    def item_reload(self, item):
        if item.type == BaseItemKind.BOXSET:
            return self.get_collection(item.name)
        if item.type == BaseItemKind.MOVIE:
            return ItemMovieWrapper(self.api.items.by_id(item.id))
    
    def delete(self, obj):
        items = self.api.items.search.recursive().add('name_starts_with', obj.name).all
        for item in items:
            if item.name == obj.name:
                LibraryApi().delete_item(item.id)
                break
        return True
        
    def fetchItem(self, data):
        warn_msg = "Jellyfin fetchItem method not implemented yet"
        logger.warning(warn_msg)
        return None
        
    def fetchItems(self, uri_args: dict | str | None = None) -> list[ItemMovieWrapper]:
        """Return items matching a Plex-style smart-filter URL.

        Kometa converts smart_filter definitions into Plex-style query args such as:
        ?type=1&sort=originallyAvailableAt:desc&push=1&genre=Action&pop=1

        Jellyfin does not consume that Plex URL directly, so we load the Jellyfin
        library items and apply the small subset of filters needed by the default
        dynamic genre collections locally.
        """
        if uri_args is None:
            return self.get_all()

        if isinstance(uri_args, str):
            from urllib.parse import parse_qs
            query_string = uri_args[1:] if uri_args.startswith("?") else uri_args
            uri_args = parse_qs(query_string)
        elif not hasattr(uri_args, "get"):
            logger.warning(f"Jellyfin fetchItems received unsupported filter args: {type(uri_args).__name__}")
            return []

        def _values(key):
            raw = uri_args.get(key)
            if raw is None:
                return []

            if not isinstance(raw, (list, tuple, set)):
                raw = [raw]

            values = []
            for value in raw:
                if value is None:
                    continue
                value = str(value).strip()
                if value:
                    values.append(value)
            return values

        def _item_values(item, attr):
            return self._metadata_names(getattr(item.item, attr, None))

        def _matches_any(item, attr, expected_values):
            actual_values = {value.casefold() for value in _item_values(item, attr)}
            return any(str(expected).casefold() in actual_values for expected in expected_values)

        search = self.api.items.search.recursive()
        search.parent_id = self.Jellyfin.id

        if self.is_movie:
            search.include_item_types = [BaseItemKind.MOVIE]
        elif self.is_show and hasattr(BaseItemKind, "SERIES"):
            search.include_item_types = [BaseItemKind.SERIES]

        field_names = ["PROVIDERIDS", "PATH", "GENRES", "TAGS", "STUDIOS"]
        fields = [getattr(ItemFields, name) for name in field_names if hasattr(ItemFields, name)]
        if fields:
            search.fields = fields

        results = [ItemMovieWrapper(item) for item in search.all]

        filter_map = {
            "genre": "genres",
            "genres": "genres",
            "label": "tags",
            "labels": "tags",
            "tag": "tags",
            "tags": "tags",
            "studio": "studios",
            "studios": "studios",
            "network": "studios",
            "networks": "studios",
            "contentRating": "official_rating",
            "content_rating": "official_rating",
            "contentrating": "official_rating",
            "year": "production_year",
        }

        for query_key, attr in filter_map.items():
            expected_values = _values(query_key)
            if not expected_values:
                continue

            if attr in ["official_rating", "production_year"]:
                expected_set = {str(value).casefold() for value in expected_values}
                results = [
                    item for item in results
                    if str(getattr(item.item, attr, "")).casefold() in expected_set
                ]
            else:
                results = [
                    item for item in results
                    if _matches_any(item, attr, expected_values)
                ]

        sort_values = _values("sort")
        if sort_values:
            sort_value = sort_values[0]
            sort_attr, _, sort_direction = sort_value.partition(":")
            reverse = sort_direction.casefold() == "desc"

            if sort_attr in ["originallyAvailableAt", "originally_available_at", "release"]:
                results.sort(
                    key=lambda item: (
                        getattr(item.item, "premiere_date", None)
                        or getattr(item.item, "production_year", None)
                        or 0,
                        item.title.casefold()
                    ),
                    reverse=reverse
                )
            elif sort_attr in ["titleSort", "title", "title_sort"]:
                results.sort(key=lambda item: item.title.casefold(), reverse=reverse)
            elif sort_attr in ["year"]:
                results.sort(key=lambda item: item.year, reverse=reverse)

        return results

    def get_tags(self, tag):
        """Return Jellyfin metadata values in a Plex FilterChoice-compatible shape.

        Kometa's dynamic collection loader calls library.get_tags("genre") and
        expects objects with title/key/tag attributes. Jellyfin does not expose
        Plex FilterChoice objects, so we derive the choices from the items in
        the active Jellyfin library and wrap each value with SimpleNamespace.
        """
        normalized_tag = str(tag).split(".", 1)[-1].lower()

        supported_tags = {
            "genre": ("genres", ["GENRES"]),
            "genres": ("genres", ["GENRES"]),
            "label": ("tags", ["TAGS"]),
            "labels": ("tags", ["TAGS"]),
            "tag": ("tags", ["TAGS"]),
            "tags": ("tags", ["TAGS"]),
            "studio": ("studios", ["STUDIOS"]),
            "studios": ("studios", ["STUDIOS"]),
            "network": ("studios", ["STUDIOS"]),
            "networks": ("studios", ["STUDIOS"]),
            "content_rating": ("official_rating", []),
            "contentrating": ("official_rating", []),
            "year": ("production_year", []),
            "years": ("production_year", []),
        }

        if normalized_tag not in supported_tags:
            logger.warning(f"Jellyfin get_tags does not support '{tag}', returning no values")
            return []

        attr, field_names = supported_tags[normalized_tag]

        search = self.api.items.search.recursive()
        search.parent_id = self.Jellyfin.id

        if self.is_movie:
            search.include_item_types = [BaseItemKind.MOVIE]
        elif self.is_show and hasattr(BaseItemKind, "SERIES"):
            search.include_item_types = [BaseItemKind.SERIES]

        fields = [getattr(ItemFields, name) for name in field_names if hasattr(ItemFields, name)]
        if fields:
            search.fields = fields

        values = {}
        for item in search.all:
            raw_values = getattr(item, attr, None)
            if raw_values is None:
                continue

            if not isinstance(raw_values, list):
                raw_values = [raw_values]

            for value in raw_values:
                name = (
                    getattr(value, "name", None)
                    or getattr(value, "Name", None)
                    or getattr(value, "tag", None)
                    or str(value)
                )
                name = str(name).strip()
                if not name or name.lower() == "none":
                    continue
                values[name.casefold()] = name

        return [
            types.SimpleNamespace(key=value, title=value, tag=value)
            for value in sorted(values.values(), key=lambda item: item.casefold())
        ]

    def get_search_choices(self, attribute, title: bool = True):
        """Return Plex-like search choices for Kometa filter validation.

        Kometa's builder validates smart_filter values by asking the library
        for the valid values for a metadata attribute. Plex returns those
        choices through the Plex API. For Jellyfin we derive the same shape
        from get_tags(), which already normalizes Jellyfin metadata values.
        """
        normalized_attribute = str(attribute).split(".", 1)[-1].lower()
        attribute_aliases = {
            "genre": "genre",
            "genres": "genre",
            "label": "label",
            "labels": "label",
            "tag": "tag",
            "tags": "tag",
            "studio": "studio",
            "studios": "studio",
            "network": "network",
            "networks": "network",
            "content_rating": "content_rating",
            "contentrating": "content_rating",
            "year": "year",
            "years": "year",
        }

        if normalized_attribute not in attribute_aliases:
            logger.warning(f"Jellyfin get_search_choices does not support '{attribute}', returning no values")
            return {}, {}

        choices = self.get_tags(attribute_aliases[normalized_attribute])
        search_choices = {}
        names = {}

        for choice in choices:
            choice_key = str(getattr(choice, "key", "")).strip()
            choice_title = str(getattr(choice, "title", choice_key)).strip()

            if not choice_key and not choice_title:
                continue

            lookup_value = choice_title if title else choice_key
            if not lookup_value:
                lookup_value = choice_key or choice_title

            search_choices[lookup_value] = choice_key or choice_title
            names[lookup_value] = choice_title or choice_key

            # Keep case-insensitive lookups available without losing display titles.
            search_choices[lookup_value.casefold()] = choice_key or choice_title
            names[lookup_value.casefold()] = choice_title or choice_key

        return search_choices, names

    def get_item_display_title(self, item) -> str:
        """Return a readable item title for overlay logging paths.

        Overlay compilation passes rating keys in some paths and wrapped items
        in others. Plex libraries expose get_item_display_title(); Jellyfin
        needs the same compatibility method so debug/trace logging does not
        abort overlay processing.
        """
        try:
            if isinstance(item, ItemMovieWrapper):
                return item.title

            if isinstance(item, Item):
                return item.name if item.name else str(item.id)

            if item in self.cached_items:
                cached_item = self.cached_items[item][0]
                return util.item_title(cached_item)

            try:
                int_item = int(item)
            except (TypeError, ValueError):
                int_item = None

            if int_item is not None and int_item in self.cached_items:
                cached_item = self.cached_items[int_item][0]
                return util.item_title(cached_item)

            return str(item)
        except Exception:
            logger.stacktrace()
            return str(item)

    def listFilterChoices(self, search_name, *args, **kwargs):
        """Return Plex-compatible filter choices for overlay label lookups.

        Kometa overlay cleanup calls self.library.Plex.listFilterChoices("label").
        PlexWrapper delegates that call back to this Jellyfin library object, so
        Jellyfin needs to expose the same method shape.
        """
        return self.get_tags(search_name)


    def edit_tags(
            self, 
            attr: str,
            obj: ItemMovieWrapper,
            add_tags: list[str] | None = None, 
            remove_tags: list[str] | None = None, 
            sync_tags: list[str] | None = None, 
            do_print: bool = True, 
            locked: bool = True, 
            is_locked: bool | None = None
        ) -> None:
        # Get the user library item
        if obj.id is None:
            return
        
        model = self.api.items.edit(obj.id)
        
        if add_tags and model.tags is None:
            model.tags = add_tags
        if add_tags and model.tags is not None:
            model.tags.extend(add_tags)
        if remove_tags:
            model.tags = [tag for tag in model.tags if tag not in remove_tags]
        if sync_tags is not None:
            model.tags = sync_tags
            
        if do_print:
            logger.info(model.tags)

        # remove duplicates
        model.tags = list(set(model.tags)) if model.tags else []
        model.lock_data = locked
        model.save()

    def find_poster_url(self, item):
        warn_msg = "Jellyfin find_poster_url method not implemented yet"
        logger.warning(warn_msg)

    def get_rating_keys(self, method, data, is_playlist=False):
        warn_msg = "Jellyfin get_rating_keys method not implemented yet"
        logger.warning(warn_msg)

    def image_update(self, item, image, tmdb=None, title=None, poster=True):
        return self._upload_image(item, image)

    def item_labels(self, item):
        pass
    
    def item_posters(self, item):
        warn_msg = "Jellyfin item_posters method not implemented yet"
        logger.warning(warn_msg)
    
    def notify_delete(self, message_id):
        warn_msg = "Jellyfin notify_delete method not implemented yet"
        logger.warning(warn_msg)

    def reload(self, item, force=False):
        if force:
            return self.fetch_item(item.id)
        return self.item_reload(item)
    
    def upload_poster(self, item, image, tmdb=None, title=None):
        return self._upload_image(item, image)
        
    def collection_order_query(self, collection, data):
        warn_msg = "Jellyfin dont support collection order"
        logger.warning(warn_msg)
        
    def find_item_assets(self, item, item_asset_directory=None, asset_directory=None, folder_name=None):
        warn_msg = "Jellyfin find_item_assets method not implemented yet"
        logger.warning(warn_msg)
        return None, None, None, item_asset_directory, folder_name

    def _upload_image(self, item: ItemMovieWrapper, image: ImageBase) -> bool:
        if image.is_poster:
            image_type = "Primary"
        elif image.is_background:
            image_type = "Backdrop"
        elif image.is_logo:
            image_type = "Logo"
        else:
            return False

        item_id = self._jellyfin_id(getattr(item, "id", None))
        if not item_id:
            raise Failed("Jellyfin Error: Cannot upload image because item has no id")

        image_location = getattr(image, "location", None)
        if not image_location:
            raise Failed("Jellyfin Error: Cannot upload image because image has no location")

        image_location = str(image_location)
        if image_location.startswith(("http://", "https://")):
            response = self.session.get(image_location, timeout=self.timeout)
            response.raise_for_status()
            image_data = response.content
            content_type = response.headers.get("Content-Type")
        else:
            with open(image_location, "rb") as image_file:
                image_data = image_file.read()
            content_type = mimetypes.guess_type(image_location)[0]

        content_type = (content_type or mimetypes.guess_type(image_location)[0] or "image/jpeg").split(";", 1)[0]
        upload_url = f"{self.url.rstrip('/')}/Items/{item_id}/Images/{image_type}"
        headers = {
            "Content-Type": content_type,
            "Accept": "application/json",
            "X-Emby-Token": self.token,
            "X-MediaBrowser-Token": self.token,
            "Authorization": f'MediaBrowser Token="{self.token}"',
        }

        params = {"api_key": self.token}
        errors = []

        for method in [self.session.post, self.session.put]:
            response = method(upload_url, headers=headers, params=params, data=image_data, timeout=self.timeout)
            if response.status_code in [200, 204]:
                return True
            errors.append(f"{method.__name__.upper()} raw returned {response.status_code}: {response.text}")

        encoded_headers = dict(headers)
        encoded_headers["Content-Type"] = "text/plain"
        encoded_data = base64.b64encode(image_data)
        for method in [self.session.post, self.session.put]:
            response = method(upload_url, headers=encoded_headers, params=params, data=encoded_data, timeout=self.timeout)
            if response.status_code in [200, 204]:
                return True
            errors.append(f"{method.__name__.upper()} base64 returned {response.status_code}: {response.text}")

        raise Failed(f"Jellyfin Error: Failed to upload {image_type} image to item {item_id}: {'; '.join(errors)}")

    def playlist_report(self):
        warn_msg = "Jellyfin playlist_report method not implemented yet"
        logger.warning(warn_msg)
        return {}
    
    def moveItem(self, obj, item, after):
        warn_msg = "Jellyfin moveItem method not implemented yet"
        logger.warning(warn_msg)

class PlexWrapper:
    def __init__(self, library: Library):
        """ Initializes PlexWrapper object """
        self.library = library
        
    @property
    def type(self) -> str:
        """ Returns the type of the library """
        # Jellyfin library types are capitalized, run_definition expect lowercase
        return self.library.type.lower()

    def __getattr__(self, name):
        return getattr(self.library, name)

class ServerWrapper:
    """ Wrapper for Jellyfin Server to match Plex Server interface """
    def __init__(self, system: jellyfin.api.system):
        """ Initializes ServerWrapper object 
        
        Args:
            system (jellyfin.api.system): The Jellyfin system object
        """
        self.system = system
        
    @property
    def machineIdentifier(self) -> str:
        """ Returns the machine identifier of the server """
        return self.system.info.id
    
    @property
    def friendlyName(self) -> str:
        """ Returns the friendly name of the server """
        return self.system.info.server_name

class ItemMovieWrapper(Movie):
    """ Wrapper for Jellyfin Movie item to match Plex Movie interface """
    
    def __init__(self, item: Item):
        """ Initializes ItemMovieWrapper object """
        self.item = item
        
    @property
    def model(self) -> BaseItemDto:
        """ Returns the underlying BaseItemDto model """
        return self.item.model

    @property
    def smart(self) -> bool:
        """ Returns False as Jellyfin does not support smart collections """
        return False
    
    @property
    def title(self) -> str:
        """ Returns the title of the movie """
        return self.item.name if self.item.name else ""
    
    @property
    def summary(self) -> str:
        """ Returns the summary of the movie """
        return self.item.overview if self.item.overview else ""

    @property
    def ratingKey(self) -> int:
        """ Returns the rating key of the movie """
        return self.item.id.int if self.item.id else 0
    
    @property
    def year(self) -> int:
        """ Returns the release year of the movie """
        return self.item.production_year if self.item.production_year else 0

    @property
    def collectionSort(self) -> int:
        """ Returns the collection sort order of the movie """
        return 0
    
    @property
    def titleSort(self) -> str:
        """ Returns the sort title of the movie """
        return self.item.sort_name if self.item.sort_name else ""

    def editSummary(self, summary: str) -> None:
        """ Edits the summary of the movie """
        self.item.overview = summary
        
    def editSortTitle(self, new_sort_title: str) -> None:
        """ Edits the sort title of the movie """
        self.item.sort_name = new_sort_title

    @staticmethod
    def _provider_id(provider_ids: dict | None, *keys: str) -> str | None:
        """Return a Jellyfin ProviderIds value using a case-insensitive key match."""
        if not provider_ids:
            return None

        wanted = {key.lower() for key in keys}
        for provider, value in provider_ids.items():
            if provider.lower() in wanted and value:
                return str(value)
        return None

    @property
    def guid(self) -> str:
        """Return a Plex-compatible primary GUID for Kometa ID mapping."""
        provider_ids = getattr(self.item, "provider_ids", None) or {}

        tmdb_id = self._provider_id(provider_ids, "Tmdb", "TMDb", "TheMovieDb", "TheMovieDB")
        if tmdb_id:
            return f"themoviedb://{tmdb_id}"

        imdb_id = self._provider_id(provider_ids, "Imdb", "IMDb")
        if imdb_id:
            return f"imdb://{imdb_id}"

        tvdb_id = self._provider_id(provider_ids, "Tvdb", "TVDb", "TheTVDb", "TheTVDB")
        if tvdb_id:
            return f"thetvdb://{tvdb_id}"

        item_id = getattr(self.item, "id", None)
        return f"local://jellyfin/{item_id}" if item_id else "local://jellyfin"

    @property
    def guids(self) -> list:
        """Return Plex-like external GUID objects for code paths that inspect item.guids."""
        provider_ids = getattr(self.item, "provider_ids", None) or {}
        guids = []

        tmdb_id = self._provider_id(provider_ids, "Tmdb", "TMDb", "TheMovieDb", "TheMovieDB")
        if tmdb_id:
            guids.append(f"themoviedb://{tmdb_id}")

        imdb_id = self._provider_id(provider_ids, "Imdb", "IMDb")
        if imdb_id:
            guids.append(f"imdb://{imdb_id}")

        tvdb_id = self._provider_id(provider_ids, "Tvdb", "TVDb", "TheTVDb", "TheTVDB")
        if tvdb_id:
            guids.append(f"thetvdb://{tvdb_id}")

        return [types.SimpleNamespace(id=guid) for guid in guids]

    @property
    def childCount(self) -> int:
        """ Returns the child count of the movie """
         # For movies, child count is typically 0
         # For collections, it would be the number of items in the collection
         # Here we return 0 for movies and actual child count for collections
        return self.item.child_count if self.item.child_count else 0
    
    def __getattr__(self, name: str) -> Any:
        if name == "guid":
            return self.guid
        if name == "guids":
            return self.guids
        return getattr(self.item, name)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ItemMovieWrapper):
            return self.ratingKey == other.ratingKey
        return False

    def __hash__(self) -> int:
        return hash(self.ratingKey)

    def __repr__(self) -> str:
        return (
            f"<ItemMovieWrapper\n  id={self.item.id}\n  ratingKey={self.ratingKey}\n  title={self.title}\n>"
        )