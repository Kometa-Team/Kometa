"""Resolve shared library definitions into independent server targets."""

from copy import deepcopy

from modules.util import Failed


def expand_libraries(libraries, media_servers, requested=None, requested_servers=None, server_types=None):
    """Intersect library selection with optional named-server and backend filters."""
    if requested_servers:
        unknown = [name for name in requested_servers if name not in media_servers]
        if unknown:
            raise Failed(f"Config Error: Requested media server(s) not defined: {', '.join(unknown)}")
    elif requested_servers is not None:
        raise Failed("Config Error: Server selection must contain nonempty server names")
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
                server_name = target.get("server") if isinstance(target, dict) else None
                if requested_servers and server_name not in requested_servers:
                    continue
                backend = getattr(media_servers.get(server_name), "type_name", None) if server_name else "plex"
                if server_types and backend not in server_types:
                    continue
                resolved.append((identity, target))
    if (requested_servers or server_types) and not resolved:
        raise Failed("Config Error: No libraries match the requested server filters")
    return resolved
