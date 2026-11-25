"""Map Plex promotion flags to Silo section definitions and acting-profile rows."""

from copy import deepcopy
from urllib.parse import quote
from uuid import NAMESPACE_URL, uuid5

from modules.util import Failed

# Read-only timestamps must not be sent back to the replacement API.
OVERRIDE_FIELDS = {
    "id",
    "section_id",
    "position",
    "hidden",
    "removed",
    "section_type",
    "title",
    "featured",
    "item_limit",
    "config",
    "is_user_added",
    "user_section_type",
    "user_config",
    "user_title",
}


class CollectionVisibility:
    def __init__(self, client, library_id):
        self.client = client
        self.library_id = str(library_id)

    def _list(self, path, params):
        data, _ = self.client.request("GET", path, params=params)
        if not isinstance(data, dict) or not isinstance(data.get("items"), list) or (data.get("page") or {}).get("has_more") or any(not isinstance(row, dict) for row in data["items"]):
            raise Failed("Silo Error: Incomplete section list; refusing to change visibility")
        return data["items"]

    def _section(self, collection, scope):
        params = {"scope": scope}
        if scope == "library":
            params["library_id"] = self.library_id
        rows = self._list("/admin/sections", params)
        if any(row.get("section_type") == "collection" and (not isinstance(row.get("config"), dict) or not isinstance(row.get("enabled"), bool)) for row in rows):
            raise Failed("Silo Error: Invalid collection section definition; refusing to change visibility")
        matches = [row for row in rows if row.get("section_type") == "collection" and str((row.get("config") or {}).get("library_collection_id")) == str(collection.id)]
        if len(matches) > 1:
            raise Failed(f"Silo Error: Collection '{collection.title}' has multiple {scope} sections; choose one row in Silo before managing visibility")
        if matches and not matches[0].get("id"):
            raise Failed("Silo Error: Collection section has no identifier")
        return matches[0] if matches else None

    def _set_section(self, collection, scope, row, enabled):
        if row is None:
            if not enabled:
                return None, False
            payload = {"scope": scope, "section_type": "collection", "title": collection.title, "config": {"library_collection_id": str(collection.id)}, "enabled": True}
            if scope == "library":
                payload["library_id"] = self.library_id
            created, _ = self.client.request("POST", "/admin/sections", json_body=payload)
            if not isinstance(created, dict) or not created.get("id"):
                raise Failed("Silo Error: Created section response has no identifier")
            return created, True
        # Never use a list response as a mutation validator. Read the canonical row.
        path = f"/admin/sections/{quote(str(row['id']), safe='')}"
        current, headers = self.client.request("GET", path)
        if not isinstance(current, dict) or any(current.get(field) != row.get(field) for field in ("scope", "library_id", "section_type", "config", "enabled", "title")):
            raise Failed("Silo Error: Collection section changed during visibility update; fetch it again")
        payload = {}
        if current.get("enabled") != enabled:
            payload["enabled"] = enabled
        if enabled and current.get("title") != collection.title:
            payload["title"] = collection.title
        if not payload:
            return current, False
        etag = headers.get("ETag") or headers.get("Etag")
        if not etag:
            raise Failed("Silo Error: Section response has no ETag; refusing to overwrite its visibility")
        updated, _ = self.client.request("PATCH", path, json_body=payload, headers={"If-Match": etag})
        return {**current, **payload, **(updated or {})}, True

    def _overrides(self):
        rows = self._list("/profile/sections", {"scope": "home"})
        if len(rows) > 500:
            raise Failed("Silo Error: Profile has too many section overrides to update safely")
        result = []
        for row in rows:
            if not isinstance(row, dict) or set(row) - OVERRIDE_FIELDS - {"created_at", "updated_at"}:
                raise Failed("Silo Error: Unrecognized profile section fields; refusing to replace profile settings")
            result.append({key: deepcopy(value) for key, value in row.items() if key in OVERRIDE_FIELDS})
        return result

    def _personal_id(self, collection):
        profile_id = self.client.server.profile_id or getattr(self.client, "_section_profile_id", None)
        if not profile_id:
            profiles = self._list("/profiles", {})
            primary = [profile.get("id") for profile in profiles if profile.get("is_primary") and profile.get("id")]
            if len(primary) != 1:
                raise Failed("Silo Error: Cannot identify the acting primary profile for Home visibility; configure profile_id")
            profile_id = primary[0]
            self.client._section_profile_id = profile_id
        return str(uuid5(NAMESPACE_URL, f"kometa:silo:home:{profile_id}:{self.library_id}:{collection.id}"))

    def update(self, collection, details):
        changed = False
        if "visible_library" in details:
            row = self._section(collection, "library")
            _, changed = self._set_section(collection, "library", row, details["visible_library"])
        if "visible_home" not in details and "visible_shared" not in details:
            return changed

        row = self._section(collection, "home")
        before = self._overrides()
        overrides = deepcopy(before)
        personal_id = self._personal_id(collection)
        personal = next((value for value in overrides if value.get("id") == personal_id), None)
        if personal and (not personal.get("is_user_added") or personal.get("user_section_type") != "collection" or str((personal.get("user_config") or {}).get("library_collection_id")) != str(collection.id)):
            raise Failed("Silo Error: Managed Home section identifier belongs to another row")
        admin_overrides = [value for value in overrides if row and value.get("section_id") == row["id"]]
        if len(admin_overrides) > 1:
            raise Failed("Silo Error: Multiple overrides for a collection Home section")
        admin_override = admin_overrides[0] if admin_overrides else None
        shared_before = bool(row and row.get("enabled"))
        home_before = bool((personal and not personal.get("hidden") and not personal.get("removed")) or (shared_before and not (admin_override and (admin_override.get("hidden") or admin_override.get("removed")))))
        shared = details.get("visible_shared", shared_before)
        home = details.get("visible_home", home_before)
        row, updated = self._set_section(collection, "home", row, shared)
        changed |= updated

        if shared:
            if row is None:
                raise Failed("Silo Error: Missing shared collection section")
            if personal:
                overrides.remove(personal)
            if admin_override:
                # Preserve the profile's other customizations, including placement.
                admin_override["hidden"] = not home
                if home:
                    admin_override["removed"] = False
            elif not home:
                overrides.append({"section_id": row["id"], "hidden": True})
        elif home:
            if personal is None:
                personal = {"id": personal_id, "is_user_added": True, "user_section_type": "collection", "user_config": {"library_collection_id": str(collection.id)}}
                overrides.append(personal)
            personal.update({"user_title": collection.title, "hidden": False, "removed": False})
        elif personal:
            overrides.remove(personal)

        if len(overrides) > 500:
            raise Failed("Silo Error: Profile has too many section overrides to update safely")
        if overrides != before:
            # This endpoint has no conditional-write support. Detect intervening
            # changes before replacing the complete set; never retry a stale set.
            if self._overrides() != before:
                raise Failed("Silo Error: Profile Home sections changed during visibility update; rerun to refresh them")
            self.client.request("PUT", "/profile/sections", params={"scope": "home"}, json_body={"overrides": overrides})
            changed = True
        return changed
