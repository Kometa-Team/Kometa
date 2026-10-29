"""Validate native rating targets and translate stored server scores."""

import math
from decimal import ROUND_HALF_UP, Decimal

from modules.util import Failed

BROWSER_RATING_FIELDS = {
    f"{server}_{slot}": (server, field, maximum) for server in ("jellyfin", "emby") for slot, field, maximum in (("community", "CommunityRating", 10), ("audience", "CommunityRating", 10), ("critic", "CriticRating", 100), ("user", "Rating", 10))
}
BROWSER_SOURCES = {source: f"Use stored {server.title()} {source.split('_', 1)[1]} rating" for source, (server, _, _) in BROWSER_RATING_FIELDS.items()}


def browser_rating_value(library, item, source):
    from modules import util

    server, field, maximum = BROWSER_RATING_FIELDS[source]
    if library.server.type_name != server:
        raise Failed(f"Rating Error: {source} requires {server}")
    value = (item.data.get("UserData") or {}).get(field) if field == "Rating" else item.data.get(field)
    return float(value) * 10 / maximum if util.is_valid_rating(value, maximum=maximum) else None


SILO_TARGETS = {"silo_imdb": "rating_imdb", "silo_tmdb": "rating_tmdb", "silo_tomatoes": "rating_rt_critic", "silo_tomatoesaudience": "rating_rt_audience", "silo_user": "user_rating"}
SILO_LABELS = {"silo_imdb": "Silo IMDB", "silo_tmdb": "Silo TMDB", "silo_tomatoes": "Silo Rotten Tomatoes", "silo_tomatoesaudience": "Silo Rotten Tomatoes Audience", "silo_user": "User Rating"}
SILO_OPERATIONS = {target: f"mass_{target}_rating_update" for target in SILO_TARGETS}
GENERIC_OPERATIONS = {name: f"mass_{name}_rating_update" for name in ("user", "critic", "audience", "episode_user", "episode_critic", "episode_audience")}
SILO_SOURCES = {target: f"Use Silo {target.removeprefix('silo_')} rating" for target in SILO_TARGETS}


def configure_rating_updates(params, server_type, logger):
    """Report incompatible options once, before scanning any library items."""
    for target, operation in {**GENERIC_OPERATIONS, **SILO_OPERATIONS}.items():
        sources = params.get(operation)
        if not sources:
            continue
        if target in SILO_TARGETS and server_type != "silo":
            logger.error(f"Config Error: ratings.{target} is unsupported on {server_type}; this target requires Silo")
            params[operation] = None
            continue
        if server_type == "silo" and target in GENERIC_OPERATIONS and target != "user":
            logger.error(f"Config Error: ratings.{target} is unsupported on Silo; use an explicit silo_imdb, silo_tmdb, silo_tomatoes, silo_tomatoesaudience, or silo_user target")
            params[operation] = None
            continue
        accepted = []
        for source in sources if isinstance(sources, list) else [sources]:
            reason = None
            if source == "clear" and server_type == "plex":
                reason = "requires a native media-server rating target"
            elif str(source).startswith(("jellyfin_", "emby_")) and (source not in BROWSER_RATING_FIELDS or BROWSER_RATING_FIELDS[source][0] != server_type):
                reason = "requires the matching Jellyfin or Emby server and a supported native rating field"
            elif source == "clear" and server_type == "jellyfin" and target in ("user", "episode_user"):
                reason = "Jellyfin ignores null numeric personal ratings; clearing this score is not supported"
            elif str(source).startswith("silo_") and server_type != "silo":
                reason = "requires Silo"
            elif str(source).startswith("plex_") and server_type != "plex":
                reason = "requires Plex provider metadata"
            elif server_type == "jellyfin" and target in ("critic", "audience", "episode_critic", "episode_audience") and source in ("lock", "unlock"):
                reason = "Jellyfin has no individual lock for this numeric rating field"
            elif server_type == "silo" and source in ("lock", "unlock", "remove", "reset", "random"):
                reason = "is not supported for native Silo rating writes; use clear to remove a rating"
            if server_type == "jellyfin" and target in ("critic", "audience", "episode_critic", "episode_audience") and source in ("remove", "reset"):
                logger.error(f"Config Error: ratings.{target} {source} lock change is unsupported on jellyfin: the rating will be cleared, but existing locks are preserved")
            if reason:
                logger.error(f"Config Error: ratings.{target} source {source} is unsupported on {server_type}: {reason}")
            else:
                accepted.append(source)
        params[operation] = accepted or None
    if server_type == "silo" and params.get(GENERIC_OPERATIONS["user"]):
        explicit = SILO_OPERATIONS["silo_user"]
        if params.get(explicit):
            logger.error("Config Error: ratings.user and ratings.silo_user both select the Silo profile rating; using ratings.silo_user")
        else:
            params[explicit] = params[GENERIC_OPERATIONS["user"]]
        params[GENERIC_OPERATIONS["user"]] = None


def rating_value(target, score):
    if score is None:
        return None
    if isinstance(score, bool):
        raise Failed("Rating Error: boolean values are not rating scores")
    try:
        number = float(score)
    except (TypeError, ValueError, OverflowError) as error:
        raise Failed(f"Rating Error: Invalid score {score}") from error
    if not math.isfinite(number) or not 0 <= number <= 10:
        raise Failed(f"Rating Error: Score {score} must be between 0 and 10")
    if target == "silo_user":
        return max(1, min(5, int((Decimal(str(number)) / 2).quantize(Decimal("1"), rounding=ROUND_HALF_UP))))
    if target in ("silo_tomatoes", "silo_tomatoesaudience"):
        return int((Decimal(str(number)) * 10).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return number


def update_silo_ratings(library, item, targets, logger):
    updates = {}
    for target, sources in targets.items():
        label = SILO_LABELS[target]
        for source in sources:
            try:
                if source == "clear":
                    score = None
                elif isinstance(source, (int, float)) and not isinstance(source, bool):
                    score = source
                elif source in ("flicklist_user", "wetrakr_user"):
                    provider = getattr(library.config, "FlickList" if source == "flicklist_user" else "WeTrakr", None)
                    if not provider:
                        raise Failed(f"{source} provider is not configured")
                    tmdb_id, tvdb_id, _ = library.get_ids(item)
                    ratings = provider.user_ratings(library.is_movie)
                    score = ratings.get(tmdb_id if library.is_movie else tvdb_id) if ratings else None
                    if score is None:
                        continue
                else:
                    variable = {"floppy": "floppy_rating", "serializd": "serializd_rating", "flicklist_user": "flicklist_user_rating", "wetrakr_user": "wetrakr_user_rating", "anidb_rating": "anidb_rating"}.get(source, f"{source}_rating")
                    score = library.fetch_overlay_value(item, variable)
                    if score is None:
                        logger.info(f"No {source} rating found for {item.title}; trying next source")
                        continue
                value = rating_value(target, score)
                field = SILO_TARGETS[target]
                if field in item.data and (item.data[field] == value or field == "user_rating" and value is None and item.data[field] == 0):
                    logger.info(f"{label} Unchanged | {value}")
                else:
                    updates[field] = value
                break
            except Failed as error:
                logger.warning(f"Silo Rating Warning: {item.title} {label} from {source}: {error}")
    for batch in ({field: value for field, value in updates.items() if field != "user_rating"}, {"user_rating": updates["user_rating"]} if "user_rating" in updates else {}):
        if not batch:
            continue
        try:
            library.update_native_ratings(item, batch)
        except Failed as error:
            logger.error(f"Silo Rating Error: {item.title} {', '.join(batch)}: {error}")
            continue
        for target, field in SILO_TARGETS.items():
            if field in batch:
                label = SILO_LABELS[target]
                logger.info(f"{label} Updated | {batch[field] if batch[field] is not None else 'cleared'}")
