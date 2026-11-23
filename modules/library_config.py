"""Resolve shared library definitions into independent server targets."""

from copy import deepcopy

from modules.util import Failed


def expand_libraries(libraries, media_servers, requested=None):
    """Return (identity, settings) pairs; select by shared name or target identity."""
    resolved = []
    identities = set()
    for name, settings in libraries.items():
        targets = settings.get("servers") if isinstance(settings, dict) else None
        if isinstance(settings, dict) and "servers" in settings:
            if "server" in settings:
                raise Failed(f"Config Error: Library {name} cannot specify both server and servers")
            if not isinstance(targets, dict) or not targets:
                raise Failed(f"Config Error: Library {name} servers must be a nonempty dictionary")
            entries = []
            for server, overrides in targets.items():
                if server not in media_servers:
                    raise Failed(f"Config Error: Library {name} server '{server}' is not defined in media_servers")
                if not isinstance(overrides, dict):
                    raise Failed(f"Config Error: Library {name} server '{server}' overrides must be a dictionary")
                if "server" in overrides or "servers" in overrides:
                    raise Failed(f"Config Error: Library {name} server '{server}' overrides cannot redefine server or servers")
                target = deepcopy({key: value for key, value in settings.items() if key != "servers"})
                target.update(deepcopy(overrides))
                target["server"] = server
                if not target.get("library_name"):
                    target["library_name"] = str(name)
                entries.append((f"{name}@{server}", target))
        else:
            entries = [(name, deepcopy(settings))]
        for identity, target in entries:
            if identity in identities or (identity != name and identity in libraries):
                raise Failed(f"Config Error: Duplicate library identity '{identity}'")
            identities.add(identity)
            if not requested or name in requested or identity in requested:
                resolved.append((identity, target))
    return resolved
