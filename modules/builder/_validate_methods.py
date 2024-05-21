from datetime import datetime
from modules import plex, util
from modules.util import Failed, FilterFailed, NotScheduled
from modules.builder._config import * 
from modules.util import Failed, FilterFailed, NonExisting, NotScheduled, NotScheduledRange

class BuilderMethodValidator:
    def validate_methods(self, collectionBuilder, methods, logger):        
        data = collectionBuilder.data
        validators = [
            self._validate_ignore_blank_results,
            self._validate_smart_label,
            self._validate_delete_not_scheduled,
            self._validate_schedule,
            self._validate_delete_collections_named,
            self._validate_collectionless,
            self._validate_builders,
            self._validate_run_again,
            self._validate_build_collection,
            self._validate_blank_collection,
            self._validateSyncMode,
            self._validate_tmdb,
            self._validate_smart_url,
            self._validate_custom_order,
        ]
        for validator in validators:
            validator(collectionBuilder, methods, data, logger)
    
    def _validate_ignore_blank_results(self, collectionBuilder, methods, data, logger):
        collectionBuilder.ignore_blank_results = False
        if "ignore_blank_results" in methods and not collectionBuilder.playlist:
            logger.debug("")
            logger.debug("Validating Method: ignore_blank_results")
            logger.debug(f"Value: {data[methods['ignore_blank_results']]}")
            collectionBuilder.ignore_blank_results = util.parse(collectionBuilder.Type, "ignore_blank_results", data, datatype="bool", methods=methods, default=False)

    def _validate_smart_label(self, collectionBuilder, methods, data, logger):
        collectionBuilder.smart_filter_details = ""
        collectionBuilder.smart_label_url = None
        collectionBuilder.smart_label = {"sort_by": "random", "all": {"label": [collectionBuilder.name]}}
        collectionBuilder.smart_label_collection = False
        if "smart_label" in methods and not collectionBuilder.playlist and not collectionBuilder.overlay and not collectionBuilder.library.is_music:
            logger.debug("")
            logger.debug("Validating Method: smart_label")
            collectionBuilder.smart_label_collection = True
            if not data[methods["smart_label"]]:
                logger.warning(f"{collectionBuilder.Type} Error: smart_label attribute is blank defaulting to random")
            else:
                logger.debug(f"Value: {data[methods['smart_label']]}")
                if isinstance(data[methods["smart_label"]], dict):
                    _data, replaced = util.replace_label(collectionBuilder.name, data[methods["smart_label"]])
                    if not replaced:
                        raise Failed("Config Error: <<smart_label>> not found in the smart_label attribute data")
                    collectionBuilder.smart_label = _data
                elif (collectionBuilder.library.is_movie and str(data[methods["smart_label"]]).lower() in plex.movie_sorts) \
                        or (collectionBuilder.library.is_show and str(data[methods["smart_label"]]).lower() in plex.show_sorts):
                    collectionBuilder.smart_label["sort_by"] = str(data[methods["smart_label"]]).lower()
                else:
                    logger.warning(f"{collectionBuilder.Type} Error: smart_label attribute: {data[methods['smart_label']]} is invalid defaulting to random")
        if collectionBuilder.smart_label_collection and collectionBuilder.library.smart_label_check(collectionBuilder.name):
            try:
                _, collectionBuilder.smart_filter_details, collectionBuilder.smart_label_url = collectionBuilder.build_filter("smart_label", collectionBuilder.smart_label, default_sort="random")
            except FilterFailed as e:
                if collectionBuilder.ignore_blank_results:
                    raise
                else:
                    raise Failed(str(e))
    
    def _validate_delete_not_scheduled(self, collectionBuilder, methods, data, logger):
        if "delete_not_scheduled" in methods and not collectionBuilder.overlay:
            logger.debug("")
            logger.debug("Validating Method: delete_not_scheduled")
            logger.debug(f"Value: {data[methods['delete_not_scheduled']]}")
            collectionBuilder.details["delete_not_scheduled"] = util.parse(collectionBuilder.Type, "delete_not_scheduled", data, datatype="bool", methods=methods, default=False)

    def _validate_schedule(self, collectionBuilder, methods, data, logger):
        if "schedule" in methods and not collectionBuilder.config.requested_collections and not collectionBuilder.overlay:
            logger.debug("")
            logger.debug("Validating Method: schedule")
            if not data[methods["schedule"]]:
                raise Failed(f"{collectionBuilder.Type} Error: schedule attribute is blank")
            else:
                logger.debug(f"Value: {data[methods['schedule']]}")
                err = None
                try:
                    util.schedule_check("schedule", data[methods["schedule"]], collectionBuilder.current_time, collectionBuilder.config.run_hour)
                except NonExisting as e:
                    collectionBuilder.non_existing = str(e)
                except NotScheduledRange as e:
                    err = e
                except NotScheduled as e:
                    if not collectionBuilder.config.ignore_schedules:
                        err = e
                if err:
                    suffix = ""
                    if collectionBuilder.details["delete_not_scheduled"]:
                        try:
                            collectionBuilder.obj = collectionBuilder.library.get_playlist(collectionBuilder.name) if collectionBuilder.playlist else collectionBuilder.library.get_collection(collectionBuilder.name, force_search=True)
                            logger.info(collectionBuilder.delete())
                            collectionBuilder.deleted = True
                            suffix = f" and was deleted"
                        except Failed:
                            suffix = f" and could not be found to delete"
                    raise NotScheduled(f"{err}\n\n{collectionBuilder.Type} {collectionBuilder.name} not scheduled to run{suffix}")

    def _validate_delete_collections_named(self, collectionBuilder, methods, data, logger):
        if "delete_collections_named" in methods and not collectionBuilder.overlay and not collectionBuilder.playlist:
            logger.debug("")
            logger.debug("Validating Method: delete_collections_named")
            logger.debug(f"Value: {data[methods['delete_collections_named']]}")
            for del_col in util.parse(collectionBuilder.Type, "delete_collections_named", data, datatype="strlist", methods=methods):
                try:
                    del_obj = collectionBuilder.library.get_collection(del_col, force_search=True)
                    collectionBuilder.library.delete(del_obj)
                    logger.info(f"Collection: {del_obj.title} deleted")
                except Failed as e:
                    if str(e).startswith("Plex Error: Failed to delete"):
                        logger.error(e)

    def _validate_collectionless(self, collectionBuilder, methods, data, logger):
        collectionBuilder.collectionless = "plex_collectionless" in methods and not collectionBuilder.playlist and not collectionBuilder.overlay

    def _validate_builders(self, collectionBuilder, methods, data, logger):
        collectionBuilder.validate_builders = True
        if "validate_builders" in methods and not collectionBuilder.overlay:
            logger.debug("")
            logger.debug("Validating Method: validate_builders")
            logger.debug(f"Value: {data[methods['validate_builders']]}")
            collectionBuilder.validate_builders = util.parse(collectionBuilder.Type, "validate_builders", data, datatype="bool", methods=methods, default=True)

    def _validate_run_again(self, collectionBuilder, methods, data, logger):
        collectionBuilder.run_again = False
        if "run_again" in methods and not collectionBuilder.overlay:
            logger.debug("")
            logger.debug("Validating Method: run_again")
            logger.debug(f"Value: {data[methods['run_again']]}")
            collectionBuilder.run_again = util.parse(collectionBuilder.Type, "run_again", data, datatype="bool", methods=methods, default=False)

    def _validate_build_collection(self, collectionBuilder, methods, data, logger):
        collectionBuilder.build_collection = False if collectionBuilder.overlay else True
        if "build_collection" in methods and not collectionBuilder.playlist and not collectionBuilder.overlay:
            logger.debug("")
            logger.debug("Validating Method: build_collection")
            logger.debug(f"Value: {data[methods['build_collection']]}")
            collectionBuilder.build_collection = util.parse(collectionBuilder.Type, "build_collection", data, datatype="bool", methods=methods, default=True)

    def _validate_blank_collection(self, collectionBuilder, methods, data, logger):
        collectionBuilder.blank_collection = False
        if "blank_collection" in methods and not collectionBuilder.playlist and not collectionBuilder.overlay:
            logger.debug("")
            logger.debug("Validating Method: blank_collection")
            logger.debug(f"Value: {data[methods['blank_collection']]}")
            collectionBuilder.blank_collection = util.parse(collectionBuilder.Type, "blank_collection", data, datatype="bool", methods=methods, default=False)

    def _validateSyncMode(self, collectionBuilder, methods, data, logger):
        collectionBuilder.sync = collectionBuilder.library.sync_mode == "sync" and collectionBuilder.type != "overlay"
        if "sync_mode" in methods and not collectionBuilder.overlay:
            logger.debug("")
            logger.debug("Validating Method: sync_mode")
            if not data[methods["sync_mode"]]:
                logger.warning(f"Collection Warning: sync_mode attribute is blank using general: {collectionBuilder.library.sync_mode}")
            else:
                logger.debug(f"Value: {data[methods['sync_mode']]}")
                if data[methods["sync_mode"]].lower() not in ["append", "sync"]:
                    logger.warning(f"Collection Warning: {data[methods['sync_mode']]} sync_mode invalid using general: {collectionBuilder.library.sync_mode}")
                else:
                    collectionBuilder.sync = data[methods["sync_mode"]].lower() == "sync"

    def _validate_tmdb(self, collectionBuilder, methods, data, logger):
        collectionBuilder.tmdb_person_offset = 0
        if "tmdb_person_offset" in methods:
            logger.debug("")
            logger.debug("Validating Method: tmdb_person_offset")
            logger.debug(f"Value: {data[methods['tmdb_person_offset']]}")
            collectionBuilder.tmdb_person_offset = util.parse(collectionBuilder.Type, "tmdb_person_offset", data, datatype="int", methods=methods, default=0, minimum=0)

        collectionBuilder.tmdb_birthday = None
        if "tmdb_birthday" in methods:
            logger.debug("")
            logger.debug("Validating Method: tmdb_birthday")
            logger.debug(f"Value: {data[methods['tmdb_birthday']]}")
            if not data[methods["tmdb_birthday"]]:
                raise Failed(f"{collectionBuilder.Type} Error: tmdb_birthday attribute is blank")
            parsed_birthday = util.parse(collectionBuilder.Type, "tmdb_birthday", data, datatype="dict", methods=methods)
            parsed_methods = {m.lower(): m for m in parsed_birthday}
            collectionBuilder.tmdb_birthday = {
                "before": util.parse(collectionBuilder.Type, "before", parsed_birthday, datatype="int", methods=parsed_methods, minimum=0, default=0),
                "after": util.parse(collectionBuilder.Type, "after", parsed_birthday, datatype="int", methods=parsed_methods, minimum=0, default=0),
                "this_month": util.parse(collectionBuilder.Type, "this_month", parsed_birthday, datatype="bool", methods=parsed_methods, default=False)
            }

        first_person = None
        collectionBuilder.tmdb_person_birthday = None
        if "tmdb_person" in methods:
            logger.debug("")
            logger.debug("Validating Method: tmdb_person")
            if not data[methods["tmdb_person"]]:
                raise Failed(f"{collectionBuilder.Type} Error: tmdb_person attribute is blank")
            else:
                logger.debug(f"Value: {data[methods['tmdb_person']]}")
                valid_names = []
                for tmdb_person in util.get_list(data[methods["tmdb_person"]]):
                    try:
                        if not first_person:
                            first_person = tmdb_person
                        person = collectionBuilder.config.TMDb.get_person(util.regex_first_int(tmdb_person, "TMDb Person ID"))
                        valid_names.append(person.name)
                        if person.biography:
                            collectionBuilder.summaries["tmdb_person"] = person.biography
                        if person.profile_url:
                            collectionBuilder.posters["tmdb_person"] = person.profile_url
                        if person.birthday and not collectionBuilder.tmdb_person_birthday:
                            collectionBuilder.tmdb_person_birthday = person.birthday
                    except Failed as e:
                        if str(e).startswith("TMDb Error"):
                            logger.error(e)
                        else:
                            try:
                                results = collectionBuilder.config.TMDb.search_people(tmdb_person)
                                if results:
                                    result_index = len(results) - 1 if collectionBuilder.tmdb_person_offset >= len(results) else collectionBuilder.tmdb_person_offset
                                    valid_names.append(tmdb_person)
                                    if results[result_index].biography:
                                        collectionBuilder.summaries["tmdb_person"] = results[result_index].biography
                                    if results[result_index].profile_url:
                                        collectionBuilder.posters["tmdb_person"] = results[result_index].profile_url
                                    if results[result_index].birthday and not collectionBuilder.tmdb_person_birthday:
                                        collectionBuilder.tmdb_person_birthday = results[result_index].birthday
                            except Failed as ee:
                                logger.error(ee)
                if len(valid_names) > 0:
                    collectionBuilder.details["tmdb_person"] = valid_names
                else:
                    raise Failed(f"{collectionBuilder.Type} Error: No valid TMDb Person IDs in {data[methods['tmdb_person']]}")

        if collectionBuilder.tmdb_birthday:
            if "tmdb_person" not in methods:
                raise NotScheduled("Skipped because tmdb_person is required when using tmdb_birthday")
            if not collectionBuilder.tmdb_person_birthday:
                raise NotScheduled(f"Skipped because No Birthday was found for {first_person}")
            now = datetime(collectionBuilder.current_time.year, collectionBuilder.current_time.month, collectionBuilder.current_time.day)

            try:
                delta = datetime(now.year, collectionBuilder.tmdb_person_birthday.month, collectionBuilder.tmdb_person_birthday.day)
            except ValueError:
                delta = datetime(now.year, collectionBuilder.tmdb_person_birthday.month, 28)

            before_delta = delta
            after_delta = delta
            if delta < now:
                try:
                    before_delta = datetime(now.year + 1, collectionBuilder.tmdb_person_birthday.month, collectionBuilder.tmdb_person_birthday.day)
                except ValueError:
                    before_delta = datetime(now.year + 1, collectionBuilder.tmdb_person_birthday.month, 28)
            elif delta > now:
                try:
                    after_delta = datetime(now.year - 1, collectionBuilder.tmdb_person_birthday.month, collectionBuilder.tmdb_person_birthday.day)
                except ValueError:
                    after_delta = datetime(now.year - 1, collectionBuilder.tmdb_person_birthday.month, 28)
            days_after = (now - after_delta).days
            days_before = (before_delta - now).days
            msg = ""
            if collectionBuilder.tmdb_birthday["this_month"]:
                if now.month != collectionBuilder.tmdb_person_birthday.month:
                    msg = f"Skipped because Birthday Month: {collectionBuilder.tmdb_person_birthday.month} is not {now.month}"
            elif days_before > collectionBuilder.tmdb_birthday["before"] and days_after > collectionBuilder.tmdb_birthday["after"]:
                msg = f"Skipped because days until {collectionBuilder.tmdb_person_birthday.month}/{collectionBuilder.tmdb_person_birthday.day}: {days_before} > {collectionBuilder.tmdb_birthday['before']} and days after {collectionBuilder.tmdb_person_birthday.month}/{collectionBuilder.tmdb_person_birthday.day}: {days_after} > {collectionBuilder.tmdb_birthday['after']}"
            if msg:
                suffix = ""
                if collectionBuilder.details["delete_not_scheduled"]:
                    try:
                        collectionBuilder.obj = collectionBuilder.library.get_playlist(collectionBuilder.name) if collectionBuilder.playlist else collectionBuilder.library.get_collection(collectionBuilder.name, force_search=True)
                        logger.info(collectionBuilder.delete())
                        collectionBuilder.deleted = True
                        suffix = f" and was deleted"
                    except Failed:
                        suffix = f" and could not be found to delete"
                raise NotScheduled(f"{msg}{suffix}")

    def _validate_smart_url(self, collectionBuilder, methods, data, logger):
        collectionBuilder.smart_url = None
        collectionBuilder.smart_type_key = None
        if "smart_url" in methods and not collectionBuilder.playlist and not collectionBuilder.overlay:
            logger.debug("")
            logger.debug("Validating Method: smart_url")
            if not data[methods["smart_url"]]:
                raise Failed(f"{collectionBuilder.Type} Error: smart_url attribute is blank")
            else:
                logger.debug(f"Value: {data[methods['smart_url']]}")
                try:
                    collectionBuilder.smart_url, collectionBuilder.smart_type_key = collectionBuilder.library.get_smart_filter_from_uri(data[methods["smart_url"]])
                except ValueError:
                    raise Failed(f"{collectionBuilder.Type} Error: smart_url is incorrectly formatted")

        if "smart_filter" in methods and not collectionBuilder.playlist and not collectionBuilder.overlay:
            try:
                collectionBuilder.smart_type_key, collectionBuilder.smart_filter_details, collectionBuilder.smart_url = collectionBuilder.build_filter("smart_filter", data[methods["smart_filter"]], display=True, default_sort="random")
            except FilterFailed as e:
                if collectionBuilder.ignore_blank_results:
                    raise
                else:
                    raise Failed(str(e))

        if collectionBuilder.collectionless:
            for x in ["smart_label", "smart_filter", "smart_url"]:
                if x in methods:
                    collectionBuilder.collectionless = False
                    logger.info("")
                    logger.warning(f"{collectionBuilder.Type} Error: {x} is not compatible with plex_collectionless removing plex_collectionless")

        if collectionBuilder.run_again and collectionBuilder.smart_url:
            collectionBuilder.run_again = False
            logger.info("")
            logger.warning(f"{collectionBuilder.Type} Error: smart_filter is not compatible with run_again removing run_again")

        if collectionBuilder.smart_url and collectionBuilder.smart_label_collection:
            raise Failed(f"{collectionBuilder.Type} Error: smart_filter is not compatible with smart_label")

        if collectionBuilder.parts_collection and "smart_url" in methods:
            raise Failed(f"{collectionBuilder.Type} Error: smart_url is not compatible with builder_level: {collectionBuilder.builder_level}")

        collectionBuilder.smart = collectionBuilder.smart_url or collectionBuilder.smart_label_collection

    def _validate_custom_order(self, collectionBuilder, methods, data, logger):
        test_sort = None
        if "collection_order" in methods and not collectionBuilder.playlist and collectionBuilder.build_collection:
            if data[methods["collection_order"]] is None:
                raise Failed(f"{collectionBuilder.Type} Warning: collection_order attribute is blank")
            else:
                test_sort = data[methods["collection_order"]]
        elif "collection_order" not in methods and not collectionBuilder.playlist and not collectionBuilder.blank_collection and collectionBuilder.build_collection and collectionBuilder.library.default_collection_order and not collectionBuilder.smart:
            test_sort = collectionBuilder.library.default_collection_order
            logger.info("")
            logger.warning(f"{collectionBuilder.Type} Warning: collection_order not found using library default_collection_order: {test_sort}")
        collectionBuilder.custom_sort = "custom" if collectionBuilder.playlist else None
        if test_sort:
            if collectionBuilder.smart:
                raise Failed(f"{collectionBuilder.Type} Error: collection_order does not work with Smart Collections")
            logger.debug("")
            logger.debug("Validating Method: collection_order")
            logger.debug(f"Value: {test_sort}")
            if test_sort in plex.collection_order_options + ["custom.asc", "custom.desc"]:
                collectionBuilder.details["collection_order"] = test_sort.split(".")[0]
                if test_sort.startswith("custom") and collectionBuilder.build_collection:
                    collectionBuilder.custom_sort = test_sort
            else:
                sort_type = collectionBuilder.builder_level
                if sort_type == "item":
                    if collectionBuilder.library.is_show:
                        sort_type = "show"
                    elif collectionBuilder.library.is_music:
                        sort_type = "artist"
                    else:
                        sort_type = "movie"
                _, _, sorts = plex.sort_types[sort_type]
                if not isinstance(test_sort, list):
                    test_sort = [test_sort]
                collectionBuilder.custom_sort = []
                for ts in test_sort:
                    if ts not in sorts:
                        raise Failed(f"{collectionBuilder.Type} Error: collection_order: {ts} is invalid. Options: {', '.join(sorts)}")
                    collectionBuilder.custom_sort.append(ts)
            if test_sort not in plex.collection_order_options + ["custom.asc", "custom.desc"] and not collectionBuilder.custom_sort:
                raise Failed(f"{collectionBuilder.Type} Error: {test_sort} collection_order invalid\n\trelease (Order Collection by release dates)\n\talpha (Order Collection Alphabetically)\n\tcustom.asc/custom.desc (Custom Order Collection)\n\tOther sorting options can be found at https://github.com/Kometa-Team/Kometa/wiki/Smart-Builders#sort-options")

        if collectionBuilder.smart:
            collectionBuilder.custom_sort = None
