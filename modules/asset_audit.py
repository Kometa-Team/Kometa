"""Report asset files and folders that no item, collection or playlist uses.

The report never changes the asset directories. Every lookup goes through the
same resolver a real run uses (``find_item_assets`` with ``read_only=True``), so
the report cannot drift from what Kometa actually uploads. When anything that
decides what is in use fails to load, no report is written: a partial list
would tell people to delete artwork that is still in use.
"""

import os
import re
from datetime import datetime

from plexapi.audio import Artist
from plexapi.video import Show

from modules import util
from modules.util import Failed

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".tbn")
SEASON_OR_EPISODE = re.compile(r"(^|_)(season\d+|s\d+e\d+)$", re.IGNORECASE)
NUMBERED_SUFFIX = re.compile(r"-\d+$")

REASON_FOLDER = "No item, collection or playlist uses this folder"
REASON_FLAT = "No item, collection or playlist matches this file name"
REASON_LOOSE = "Loose file outside any asset folder; with asset_folders enabled Kometa only reads files inside an item's folder"
REASON_SEASON = "No matching season or episode in the library"
REASON_NAME = "Kometa does not use this file name in this folder"
REASON_DUPLICATE = "Another file with the same name is used instead: {used}"


def _key(path):
    # realpath so the same folder reached through a symlink or another configured spelling compares equal.
    return os.path.normcase(os.path.realpath(path))


def _directories(library):
    return [d for d in list(library.asset_directory or []) + list(library.collection_asset_directory or []) if d]


def _human_size(size):
    value = float(size)
    for unit in ["B", "KB", "MB", "GB"]:
        if value < 1024 or unit == "GB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} GB"


def _is_hidden(name):
    return name.startswith((".", "@"))


class _Claims:
    """Paths a real run would read: matched image files and resolved asset folders."""

    def __init__(self):
        self.files = set()
        self.folders = set()
        # Folders as the resolver reached them, before symlinks are resolved, so the folders holding a link stay used.
        self.folder_paths = set()

    def add(self, result):
        poster, background, logo, square_art, item_dir, _ = result
        for image in (poster, background, logo, square_art):
            if image is not None and getattr(image, "location", None):
                self.files.add(_key(image.location))
        if item_dir:
            self.folders.add(_key(item_dir))
            self.folder_paths.add(os.path.abspath(item_dir))
        return item_dir, result[5]


def _resolve(library, claims, item, **kwargs):
    try:
        return claims.add(library.find_item_assets(item, read_only=True, **kwargs))
    except Failed:
        # No asset folder for this item: it uses nothing, which is what a real run sees too.
        return None, None


def _claim_item(library, claims, item):
    """Mirror the traversal in ``Plex.find_and_upload_assets``, searching the library's own directories as a real run does."""
    item_dir, name = _resolve(library, claims, item)
    item_type = getattr(item, "type", None)
    if (isinstance(item, Show) or item_type == "show") and ((library.asset_folders and item_dir) or not library.asset_folders):
        for season in library.query(item.seasons):
            _resolve(library, claims, season, item_asset_directory=item_dir, folder_name=name)
            for episode in library.query(season.episodes):
                if getattr(episode, "seasonEpisode", None):
                    _resolve(library, claims, episode, item_asset_directory=item_dir, folder_name=name)
    elif isinstance(item, Artist) or item_type == "artist":
        for album in library.query(item.albums):
            _resolve(library, claims, album, item_asset_directory=item_dir, folder_name=name)


def _path_list(value):
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, (list, tuple)):
        return [v for v in value if isinstance(v, str) and v]
    return []


def _definition_value(file, mapping_name, data, attribute):
    """Read a definition attribute as the builder does: keys in any case, and values a template supplies."""
    if not isinstance(data, dict):
        return None
    methods = {str(key).lower(): key for key in data}
    if attribute in methods:
        return data[methods[attribute]]
    if "template" in methods and callable(getattr(file, "apply_template", None)):
        variables = data[methods["variables"]] if "variables" in methods and isinstance(data[methods["variables"]], dict) else {}
        explicit_name = data[methods["name"]] if "name" in methods else None
        try:
            expanded = file.apply_template(explicit_name, mapping_name, data, data[methods["template"]], variables)
        except Failed as e:
            raise Failed(f"could not expand the templates of {mapping_name}: {e}") from e
        for key, value in (expanded or {}).items():
            if str(key).lower() == attribute:
                return value
    return None


def _override_directories(library, files, entries_attribute):
    """Asset directories set on collection or playlist files and on single definitions inside them."""
    directories = []
    for file in files:
        directories.extend(_path_list(getattr(file, "asset_directory", None)))
        directories.extend(_path_list(getattr(file, "collection_asset_directory", None)))
        for mapping_name, data in (getattr(file, entries_attribute, None) or {}).items():
            value = _definition_value(file, mapping_name, data, "asset_directory")
            if not value:
                continue
            try:
                items, collections = util.resolve_asset_directories(util.asset_directory_paths(value), library.type)
            except Failed:
                # A real run rejects this value too, so the definition reads no assets from it.
                continue
            directories.extend(_path_list(collections) + _path_list(items))
    return directories


def _playlist_files(config):
    return list(getattr(config, "playlist_files", None) or []) + list(getattr(config, "unscheduled_playlist_files", None) or [])


def _playlist_names(config):
    names = set(getattr(config, "playlist_names", None) or [])
    for playlist_file in _playlist_files(config):
        for mapping_name, data in (getattr(playlist_file, "playlists", None) or {}).items():
            names.add(str(mapping_name))
            name_mapping = _definition_value(playlist_file, mapping_name, data, "name_mapping")
            if name_mapping:
                names.add(str(name_mapping))
    return names


def _contains(parent, child):
    try:
        return os.path.commonpath([parent, child]) == parent
    except ValueError:
        # Different drives on Windows.
        return False


def _shares_directories(directories, other):
    """True when any directory of one list is the same as, inside, or contains one of the other."""
    keys = {_key(d) for d in directories}
    return any(_contains(a, b) or _contains(b, a) for a in keys for b in {_key(d) for d in other})


def incomplete_reasons(config, libraries):
    """Why the set of things that use assets cannot be known in full this run."""
    reasons = []
    filters = [flag for flag, value in (("--run-libraries", "requested_libraries"), ("--run-servers", "requested_servers"), ("a server-type filter", "requested_server_types")) if getattr(config, value, None)]
    if filters:
        reasons.append(f"the run is limited by {' and '.join(filters)}, so other libraries sharing the asset directories are not loaded")
    failed = getattr(config, "failed_libraries", None) or []
    if failed:
        reasons.append(f"these libraries failed to connect: {', '.join(map(str, failed))}")
    for lib in libraries:
        files = getattr(lib, "incomplete_collection_files", None) or []
        if files:
            reasons.append(f"collection files for the {lib.name} library did not load: {', '.join(map(str, files))}")
    playlists = getattr(config, "incomplete_playlist_files", None) or []
    if playlists:
        reasons.append(f"playlist files did not load: {', '.join(map(str, playlists))}")
    return reasons


def sharing_libraries(config, library, directories):
    libraries = [lib for lib in getattr(config, "libraries", None) or [] if lib is library or _shares_directories(directories, _directories(lib))]
    if library not in libraries:
        libraries.insert(0, library)
    return libraries


def collect_claims(config, library, directories, collection_names_for, logger):
    """Resolve every item, collection and playlist of each library sharing ``directories``.

    Raises ``Failed`` when any of them cannot be loaded.
    """
    claims = _Claims()
    libraries = sharing_libraries(config, library, directories)
    reasons = incomplete_reasons(config, libraries)
    if reasons:
        raise Failed(f"Unused Assets Report Error: Cannot tell which assets are in use because {'; '.join(reasons)}. No report was written.")
    checked = []
    for lib in libraries:
        logger.info(f"Checking assets used by the {lib.name} library")
        try:
            items = lib.get_all(ignore_schedule_scope=True)
            for i, item in enumerate(items, 1):
                logger.ghost(f"Checking Assets: {i}/{len(items)} {item.title}")
                _claim_item(lib, claims, item)
            logger.exorcise()
            names = {str(name) for name in collection_names_for(lib)}
            names.update(str(collection.title) for collection in lib.get_all_collections())
            # A collection may read from collection directories, item directories or file overrides; check each on its own
            # so a same-named folder in one directory cannot hide the folder a real run would use in another.
            search = _unique(list(directories) + _directories(lib) + _override_directories(lib, getattr(lib, "configured_collection_metadata_files", None) or [], "collections"))
        except Failed as e:
            raise Failed(f"Unused Assets Report Error: Could not load everything the {lib.name} library uses ({e}). No report was written.") from e
        for name in sorted(names):
            for directory in search:
                _resolve(lib, claims, name, asset_directory=[directory])
        checked.append(lib.name)
    try:
        search = _unique(list(directories) + _override_directories(library, _playlist_files(config), "playlists"))
        playlist_names = _playlist_names(config)
    except Failed as e:
        raise Failed(f"Unused Assets Report Error: Could not read every playlist ({e}). No report was written.") from e
    for name in sorted(playlist_names):
        for directory in search:
            _resolve(library, claims, name, asset_directory=[directory])
    return claims, checked


def _unique(directories):
    seen = set()
    result = []
    for directory in directories:
        if _key(directory) not in seen:
            seen.add(_key(directory))
            result.append(directory)
    return result


def _file_reason(filename, in_item_folder, used_here, asset_folders):
    if not in_item_folder:
        return REASON_LOOSE if asset_folders else REASON_FLAT
    base_stem = NUMBERED_SUFFIX.sub("", os.path.splitext(filename)[0]).lower()
    if base_stem in used_here:
        return REASON_DUPLICATE.format(used=used_here[base_stem])
    if SEASON_OR_EPISODE.search(base_stem):
        return REASON_SEASON
    return REASON_NAME if asset_folders else REASON_FLAT


def find_unused(directories, claims, asset_folders):
    """Walk ``directories`` and return (unused_folders, unused_files) as lists of dicts."""
    used_folders = set()

    def mark_used(folder):
        current = folder
        while current not in used_folders:
            used_folders.add(current)
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent

    for folder in claims.folders:
        mark_used(folder)
    for path in claims.folder_paths:
        # Walk up the unresolved path: a folder holding a symlink to an asset folder must not be reported, or deleting it breaks the link.
        current = path
        while True:
            used_folders.add(_key(current))
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
    # A scanned root nested inside another is walked on its own, and the folders above it are never unused.
    root_keys = {_key(d) for d in directories if os.path.isdir(d)}
    for root_key in root_keys:
        mark_used(os.path.dirname(root_key))
    unused_folders = []
    unused_files = []
    seen_roots = set()
    for root_dir in directories:
        root_key = _key(root_dir)
        if root_key in seen_roots or root_key not in root_keys:
            continue
        seen_roots.add(root_key)
        for current, dirnames, filenames in os.walk(root_dir):
            current_key = _key(current)
            keep = []
            for dirname in sorted(dirnames):
                path = os.path.join(current, dirname)
                if _is_hidden(dirname) or _key(path) in root_keys:
                    continue
                if _key(path) in used_folders:
                    keep.append(dirname)
                else:
                    count, size = _folder_totals(path)
                    if count:
                        unused_folders.append({"path": os.path.abspath(path), "files": count, "size": _human_size(size), "bytes": size, "reason": REASON_FOLDER})
            dirnames[:] = keep
            # With asset_folders, files are read only from an item's own folder; without it, only from the root.
            in_item_folder = (current_key in claims.folders and current_key != root_key) if asset_folders else current_key == root_key
            used_here = {}
            for filename in sorted(filenames):
                if _key(os.path.join(current, filename)) in claims.files:
                    used_here.setdefault(NUMBERED_SUFFIX.sub("", os.path.splitext(filename)[0]).lower(), filename)
            for filename in sorted(filenames):
                full = os.path.join(current, filename)
                if _is_hidden(filename) or os.path.splitext(filename)[1].lower() not in IMAGE_EXTENSIONS or _key(full) in claims.files:
                    continue
                size = os.path.getsize(full)
                unused_files.append({"path": os.path.abspath(full), "size": _human_size(size), "bytes": size, "reason": _file_reason(filename, in_item_folder, used_here, asset_folders)})
    return unused_folders, unused_files


def _folder_totals(path):
    count = 0
    size = 0
    for current, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if not _is_hidden(d)]
        for filename in filenames:
            if not _is_hidden(filename) and os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS:
                count += 1
                size += os.path.getsize(os.path.join(current, filename))
    return count, size


def run_unused_assets_report(config, library, collection_names_for, logger):
    """Write the library's unused assets report; returns the report data, or None when none was written."""
    settings = library.unused_assets_report
    path = settings["path"]
    logger.info("")
    logger.separator(f"Unused Assets Report for {library.name} Library", space=False, border=False)
    logger.info("")
    directories = []
    for directory in _directories(library):
        if _key(directory) not in {_key(d) for d in directories}:
            directories.append(directory)
    existing = [d for d in directories if os.path.isdir(d)]
    for missing in [d for d in directories if not os.path.isdir(d)]:
        logger.warning(f"Unused Assets Report Warning: Asset directory not found: {os.path.abspath(missing)}")
    if not existing:
        logger.error("Unused Assets Report Error: No asset directory to check. Set asset_directory for this library or in settings. No report was written.")
        return None
    try:
        claims, checked = collect_claims(config, library, existing, collection_names_for, logger)
    except Failed as e:
        logger.error(e)
        return None
    except Exception as e:
        logger.stacktrace()
        logger.error(f"Unused Assets Report Error: {e}. No report was written.")
        return None
    unused_folders, unused_files = find_unused(existing, claims, library.asset_folders)
    total = sum(f["bytes"] for f in unused_folders) + sum(f["bytes"] for f in unused_files)
    data = {
        "library": library.name,
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "asset_directories": [os.path.abspath(d) for d in existing],
        "libraries_checked": checked,
        "summary": {"unused_folders": len(unused_folders), "unused_files": len(unused_files), "total_size": _human_size(total)},
        "unused_folders": [{k: v for k, v in f.items() if k != "bytes"} for f in unused_folders],
        "unused_files": [{k: v for k, v in f.items() if k != "bytes"} for f in unused_files],
    }
    yaml = config.Requests.file_yaml(path, create=True, start_empty=True)
    yaml.data = data
    yaml.save()
    logger.info(f"Unused Assets: {len(unused_folders)} folder{'' if len(unused_folders) == 1 else 's'} and {len(unused_files)} file{'' if len(unused_files) == 1 else 's'} ({_human_size(total)})")
    logger.info(f"Unused Assets Report saved to {os.path.abspath(path)}")
    return data
