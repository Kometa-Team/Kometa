from json import JSONDecodeError
from modules import util
from modules.util import Failed

logger = util.logger

class Webhooks:
    def __init__(self, config, system_webhooks, library=None, notifiarr=None, gotify=None):
        self.config = config
        self.requests = self.config.Requests
        self.error_webhooks = system_webhooks["error"] if "error" in system_webhooks else []
        self.version_webhooks = system_webhooks["version"] if "version" in system_webhooks else []
        self.run_start_webhooks = system_webhooks["run_start"] if "run_start" in system_webhooks else []
        self.run_end_webhooks = system_webhooks["run_end"] if "run_end" in system_webhooks else []
        self.delete_webhooks = system_webhooks["delete"] if "delete" in system_webhooks else []
        self.library = library
        self.notifiarr = notifiarr
        self.gotify = gotify

    def _request(self, webhooks, json):
        logger.trace("")
        logger.separator("Webhooks", space=False, border=False, trace=True)
        logger.trace("")
        json["library_mapping_name"] = self.library.mapping_name if self.library else ""
        logger.trace(f"JSON: {json}")
        for webhook in list(set(webhooks)):
            response = None
            logger.trace(f"Webhook: {webhook}")
            if webhook == "notifiarr":
                if self.notifiarr:
                    for x in range(6):
                        response = self.notifiarr.notification(json)
                        if response.status_code < 500:
                            break
            elif webhook == "gotify":
                if self.gotify:
                    self.gotify.notification(json)
            else:
                if webhook.startswith("https://discord.com/api/webhooks"):
                    json = self.discord(json)
                elif webhook.startswith("https://hooks.slack.com/services"):
                    json = self.slack(json)
                response = self.requests.post(webhook, json=json)
            if response is not None:
                try:
                    response_json = response.json()
                    logger.trace(f"Response: {response_json}")
                    if webhook == "notifiarr" and self.notifiarr and response.status_code == 400:
                        def remove_from_config(text, hook_cat):
                            if response_json["details"]["response"] == text:
                                yaml = self.requests.file_yaml(self.config.config_path)
                                changed = False
                                if hook_cat in yaml.data and yaml.data["webhooks"][hook_cat]:
                                    if isinstance(yaml.data["webhooks"][hook_cat], list) and "notifiarr" in yaml.data["webhooks"][hook_cat]:
                                        changed = True
                                        yaml.data["webhooks"][hook_cat].pop("notifiarr")
                                    elif yaml.data["webhooks"][hook_cat] == "notifiarr":
                                        changed = True
                                        yaml.data["webhooks"][hook_cat] = None
                                if changed:
                                    yaml.save()
                        remove_from_config("Kometa updated trigger is not enabled", "changes")
                        remove_from_config("Kometa created trigger is not enabled", "changes")
                        remove_from_config("Kometa deleted trigger is not enabled", "changes")
                        remove_from_config("Kometa failure trigger is not enabled", "error")
                        remove_from_config("Kometa start/complete trigger is not enabled", "run_start")
                        remove_from_config("Kometa start/complete trigger is not enabled", "run_end")
                        remove_from_config("Kometa app updates trigger is not enabled", "version")
                    if "result" in response_json and response_json["result"] == "error" and "details" in response_json and "response" in response_json["details"]:
                        raise Failed(f"Notifiarr Error: {response_json['details']['response']}")
                    if response.status_code >= 400 or ("result" in response_json and response_json["result"] == "error"):
                        raise Failed(f"({response.status_code} [{response.reason}]) {response_json}")
                except JSONDecodeError:
                    if response.status_code >= 400:
                        raise Failed(f"({response.status_code} [{response.reason}])")

    def start_time_hooks(self, start_time):
        if self.run_start_webhooks:
            self._request(self.run_start_webhooks, {"event": "run_start", "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S")})

    def version_hooks(self):
        if self.version_webhooks:
            notes = None
            if self.requests.local.main != self.requests.latest.main:
                notes = self.config.GitHub.latest_release_notes()
            elif self.requests.local.build and self.requests.local.build < self.requests.latest.build:
                notes = self.config.GitHub.get_commits(self.requests.local.build, nightly=self.requests.branch == "nightly")
            self._request(self.version_webhooks, {"event": "version", "current": str(self.requests.local), "latest": str(self.requests.latest), "notes": notes})

    def end_time_hooks(self, start_time, end_time, run_time, stats):
        if self.run_end_webhooks:
            self._request(self.run_end_webhooks, {
                "event": "run_end",
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "run_time": run_time,
                "collections_created": stats["created"],
                "collections_modified": stats["modified"],
                "collections_deleted": stats["deleted"],
                "items_added": stats["added"],
                "items_removed": stats["removed"],
                "added_to_radarr": stats["radarr"],
                "added_to_sonarr": stats["sonarr"],
                "names": stats["names"]
            })

    def error_hooks(self, text, server=None, library=None, collection=None, playlist=None, critical=True):
        if self.error_webhooks:
            json = {"event": "error", "error": str(text), "critical": critical}
            if server:          json["server_name"] = str(server)
            if library:         json["library_name"] = str(library)
            if collection:      json["collection"] = str(collection)
            if playlist:        json["playlist"] = str(playlist)
            self._request(self.error_webhooks, json)

    def delete_hooks(self, message, server=None, library=None):
        if self.delete_webhooks:
            json = {"event": "delete", "message": str(message)}
            if server:          json["server_name"] = str(server)
            if library:         json["library_name"] = str(library)
            self._request(self.delete_webhooks, json)

    def collection_hooks(self, webhooks, collection, poster_url=None, background_url=None, created=False,
                         additions=None, removals=None, radarr=None, sonarr=None, playlist=False):
        if self.library:
            thumb = None
            if not poster_url and collection.thumb and next((f for f in collection.fields if f.name == "thumb"), None):
                thumb = self.requests.get_image_encoded(f"{self.library.url}{collection.thumb}?X-Plex-Token={self.library.token}")
            art = None
            if not playlist and not background_url and collection.art and next((f for f in collection.fields if f.name == "art"), None):
                art = self.requests.get_image_encoded(f"{self.library.url}{collection.art}?X-Plex-Token={self.library.token}")
            self._request(webhooks, {
                "event": "changes",
                "server_name": self.library.PlexServer.friendlyName,
                "library_name": self.library.name,
                "playlist" if playlist else "collection": collection.title,
                "created": created,
                "poster": thumb,
                "background": art,
                "poster_url": poster_url,
                "background_url": background_url,
                "additions": additions if additions else [],
                "removals": removals if removals else [],
                "radarr_adds": radarr if radarr else [],
                "sonarr_adds": sonarr if sonarr else [],
            })

    def slack(self, json):
        if json["event"] == "run_end":
            title = ":white_check_mark: Kometa Has Finished a Run"
            rows = [
                [("*Start Time*", json["start_time"]), ("*End Time*", json["end_time"]), ("*Run Time*", json["run_time"])],
                [],
                [
                    (":heavy_plus_sign: *Collections Created*", str(json["collections_created"])),
                    (":infinity: *Collections Modified*", str(json["collections_modified"])),
                    (":heavy_minus_sign: *Collections Deleted*", str(json["collections_deleted"]))
                ]
            ]
            if json["added_to_radarr"] or json["added_to_sonarr"]:
                rows.append([])
            if json["added_to_radarr"]:
                rows.append([("*Added To Radarr*", json['added_to_radarr'])])
            if json["added_to_sonarr"]:
                rows.append([("*Added To Sonarr*", json['added_to_sonarr'])])

        elif json["event"] == "run_start":
            title = ":information_source: Kometa Has Started!"
            rows = [[("*Start Time*", json["start_time"])]]
        elif json["event"] == "version":
            title = "Kometa Has a New Version Available"
            rows = [
                [("*Current Version*", json["current"]), ("*Latest Version*", json["latest"])],
                [(json["notes"], )]
            ]
        else:
            rows = []
            row1 = []
            text = ""
            if "server_name" in json:
                row1.append(("*Server Name*", json["server_name"]))
            if "library_name" in json:
                row1.append(("*Library Name*", json["library_name"]))
            if "collection" in json:
                text = "Collection"
                row1.append(("*Collection Name*", json["collection"]))
            elif "playlist" in json:
                text = "Playlist"
                row1.append(("*Playlist Name*", json["playlist"]))
            if row1:
                rows.append(row1)
            if json["event"] == "delete":
                title = json["message"]
            elif "error" in json:
                title = f":warning: Kometa Encountered {'a Critical' if json['critical'] else 'an'} Error"
                rows.append([])
                rows.append([(json["error"], )])
            else:
                title = f"{':heavy_plus_sign:' if json['created'] else ':infinity:'} A {text} has Been {'Created' if json['created'] else 'Modified'}!"

                def get_field_text(items_list):
                    field_text = ""
                    for i, item in enumerate(items_list, 1):
                        if "tmdb_id" in item:
                            field_text += f"\n{i}. [{item['title']}](https://www.themoviedb.org/movie/{item['tmdb_id']})"
                        elif "tvdb_id" in item:
                            field_text += f"\n{i}. [{item['title']}](https://www.thetvdb.com/dereferrer/series/{item['tvdb_id']})"
                        else:
                            field_text += f"\n{i}. {item['title']}"
                    return field_text

                if json["additions"]:
                    rows.append([])
                    rows.append([("*Items Added*", " ")])
                    rows.append([(get_field_text(json["additions"]), )])
                if json["removals"]:
                    rows.append([])
                    rows.append([("*Items Removed*", " ")])
                    rows.append([(get_field_text(json["removals"]), )])

        new_json = {
            "text": title,
            "blocks": [{
                "type": "header",
                "text": {"type": "plain_text", "text": title}
            }]
        }

        if rows:
            for row in rows:
                if row:
                    if len(row[0]) == 1:
                        section = {"type": "section", "text": {"type": "plain_text", "text": row[0][0]}}
                        new_json["blocks"].append(section)
                    else:
                        section = {"type": "section", "fields": []}
                        for col in row:
                            section["fields"].append({"type": "mrkdwn", "text": col[0]})
                            section["fields"].append({"type": "plain_text", "text": col[1]})
                        new_json["blocks"].append(section) # noqa
                else:
                    new_json["blocks"].append({"type": "divider"}) # noqa
        return new_json

    def discord(self, json):
        description = None
        rows = []
        if json["event"] == "run_end":
            title = "Run Completed"
            rows = [
                [("Start Time", json["start_time"]), ("End Time", json["end_time"]), ("Run Time", json["run_time"])],
                [("Collections", None)],
                [
                    ("Created", json["collections_created"] if json["collections_created"] else "0"),
                    ("Modified", json["collections_modified"] if json["collections_modified"] else "0"),
                    ("Deleted", json["collections_deleted"] if json["collections_deleted"] else "0")
                ]
            ]
            if json["added_to_radarr"]:
                rows.append([(f"{json['added_to_radarr']} Movies Added To Radarr", None)])
            if json["added_to_sonarr"]:
                rows.append([(f"{json['added_to_sonarr']} Series Added To Sonarr", None)])
        elif json["event"] == "run_start":
            title = "Run Started"
            description = json["start_time"]
        elif json["event"] == "version":
            title = "New Version Available"
            rows = [
                [("Current", json["current"]), ("Latest", json["latest"])],
                [("New Commits", json["notes"])]
            ]
        else:
            row1 = []
            text = ""
            if "server_name" in json:
                row1.append(("Server", json["server_name"]))
            if "library_name" in json:
                row1.append(("Library", json["library_name"]))
            if "collection" in json:
                text = "Collection"
                row1.append(("Collection", json["collection"]))
            elif "playlist" in json:
                text = "Playlist"
                row1.append(("Playlist", json["playlist"]))
            if row1:
                rows.append(row1)
            if json["event"] == "delete":
                title = json["message"]
            elif "error" in json:
                title = f"{'Critical ' if json['critical'] else ''}Error"
                rows.append([("Error Message", json["error"])])
            else:
                title = f"{text} {'Created' if json['created'] else 'Modified'}"

                def get_field_text(items_list):
                    field_text = ""
                    for i, item in enumerate(items_list, 1):
                        if "tmdb_id" in item:
                            field_text += f"\n{i}. [{item['title']}](https://www.themoviedb.org/movie/{item['tmdb_id']})"
                        elif "tvdb_id" in item:
                            field_text += f"\n{i}. [{item['title']}](https://www.thetvdb.com/dereferrer/series/{item['tvdb_id']})"
                        else:
                            field_text += f"\n{i}. {item['title']}"
                    return field_text

                if json["additions"]:
                    rows.append([("Items Added", get_field_text(json["additions"]))])
                if json["removals"]:
                    rows.append([("Items Removed", get_field_text(json["removals"]))])
        new_json = {
            "embeds": [
                {
                    "title": title,
                    "color": 0x00bc8c
                }
            ],
            "username": "Kobota",
            "avatar_url": "https://github.com/Kometa-Team/Kometa/raw/master/.github/bot.png"
        }
        if description:
            new_json["embeds"][0]["description"] = description

        if rows:
            fields = []
            for row in rows:
                for col in row:
                    col_name, col_value = col
                    field = {"name": col_name, "value": col_value if col_value else ""}
                    if len(row) > 1:
                        field["inline"] = True
                    fields.append(field)
            new_json["embeds"][0]["fields"] = fields
        return new_json
