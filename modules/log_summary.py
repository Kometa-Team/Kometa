import re
from collections import Counter, defaultdict
from dataclasses import dataclass

SEVERITIES = ("WARNING", "ERROR", "CRITICAL")


@dataclass(frozen=True)
class DetailedSummaryRule:
    section: str
    prefix: str
    pattern: str
    message: str
    detail_group: str | None = "detail"


SUMMARY_NORMALIZATIONS = [
    (r"AniDB Error: No valid AniDB IDs found in input: .+", "AniDB Error: No valid AniDB IDs found in input"),
    (r"AniList Error: No valid AniList IDs in .+", "AniList Error: No valid AniList IDs"),
    (r"Asset Warning: Asset Directory Not Found and Created: .+", "Asset Warning: Asset Directory Not Found and Created"),
    (r"Asset Warning: No supported artwork found in the assets folder '.+'", "Asset Warning: No supported artwork found in the assets folder"),
    (r"Asset Warning: No poster found for '.+' in the assets folder '.+'", "Asset Warning: No poster found in assets"),
    (r"Asset Warning: No poster '.+' found in the assets folders", "Asset Warning: No poster found in assets"),
    (r"Asset Warning: No poster or background found in an assets folder for '.+'", "Asset Warning: No poster or background found in an assets folder"),
    (r"Asset Warning: Unable to find asset folder: '.+'", "Asset Warning: Unable to find asset folder"),
    (r"Collection Error: No valid Plex Collections in .+", "Collection Error: No valid Plex Collections"),
    (r"Config Warning: Skipping duplicate ([^:]+): .+", r"Config Warning: Skipping duplicate \1"),
    (r"Skipping .+: Item not found(?: in .+)?$", "Item not found"),
    (r"(?:Collection|Playlist) Warning: tvdb_episode:\d+_\d+_\d+ -> .+ Season: \d+ Episode: \d+ Missing", "TVDb Episode Missing"),
    (r"(?:Collection|Playlist) Warning: tvdb_season:\d+_\d+ -> .+ Season: \d+ Missing", "TVDb Season Missing"),
    (r"(?:Collection|Playlist) Warning: imdb:tt\d+ -> .+ Season: \d+ Episode: \d+ Missing", "IMDb Episode Missing"),
    (r".+ Error: Background Path Does Not Exist: .+", "Error: Background Path Does Not Exist"),
    (r".+ Error: Logo Path Does Not Exist: .+", "Error: Logo Path Does Not Exist"),
    (r".+ Error: Poster Path Does Not Exist: .+", "Error: Poster Path Does Not Exist"),
    (r".+ Error: Square Art Path Does Not Exist: .+", "Error: Square Art Path Does Not Exist"),
    (r".+ Error: Theme Path Does Not Exist: .+", "Error: Theme Path Does Not Exist"),
    (r".+ Error: No builders were found", "Error: No builders were found"),
    (r".+ Error: No Plex Filter Created", "Error: No Plex Filter Created"),
    (r"Letterboxd Error: No List Items found in .+", "Letterboxd Error: No List Items found"),
    (r"Letterboxd Error: TMDb Movie ID not found at .+ item is type .+ with tmdb_id .+\.", "Letterboxd Error: TMDb Movie ID not found"),
    (r"Letterboxd Warning: cloudscraper hit a Cloudflare challenge for .+; retrying with curl_cffi\.", "Letterboxd Warning: Cloudflare challenge; retrying with curl_cffi"),
    (r"Letterboxd Warning: letterboxdpy does not reliably support films page .+; using Kometa fallback parsing\.", "Letterboxd Warning: Using fallback films-page parsing"),
    (r"Letterboxd Warning: TMDb link for .+ is for a TV show, not a movie; ignoring TMDb ID .+ from link\.", "Letterboxd Warning: TMDb link is for a TV show, not a movie"),
    (r"MDBList Warning: Batch lookup returned no data for \d+ of \d+ requested [A-Za-z]+ IDs: .+", "MDBList Warning: Batch lookup returned no data for requested IDs"),
    (r"MDBList Warning: Skipping .+: Convert Warning: No TMDb ID found for TVDb ID '.+'", "MDBList Warning: Skipping item because no TMDb ID was found"),
    (r"Mojo Error: No List Items found in .+", "Mojo Error: No List Items found"),
    (r"No MdbItem for .+ \(Guid: .+\)", "MDBList Warning: No item found"),
    (r"Text File Error: No IDs found at .+", "Text File Error: No IDs found"),
    (r"Text File Error: No supported IDs found in .+", "Text File Error: No supported IDs found"),
    (r"TMDb Error: Collection ID \d+ missing on TMDb; add '\d+' to the franchise exclude list if this is auto-built\.", "TMDb Error: Collection ID missing on TMDb; add it to the franchise exclude list if this is auto-built"),
    (r"TMDb Error: No Episode found for TMDb ID \d+ Season \d+ Episode \d+: .+", "TMDb Error: No Episode found for TMDb ID"),
    (r"TMDb Error: No Movie found for TMDb ID:? \d+(?:: .+)?", "TMDb Error: No Movie found for TMDb ID"),
    (r"TMDb Error: No valid TMDb IDs in .+", "TMDb Error: No valid TMDb IDs"),
    (r"TMDb Warning: unable to load (movie|show) TMDb ID \d+; skipping item: (.+)", r"TMDb Warning: Unable to load \1; skipping item: \2"),
    (r"TVDb Error: No TVDb IDs found at .+", "TVDb Error: No TVDb IDs found"),
    (r"TVDb Error: Skipping Movie: .+", "TVDb Error: Skipping movie"),
    (r"FlickList Warning: No usable ID found for .+; skipping", "FlickList Warning: No usable ID found; skipping item"),
    (r"Plex Warning: Collection '.+' already exists; skipping creation", "Plex Warning: Collection already exists; skipping creation"),
    (r"Plex Warning: Unable to batch (.+) update for .+; using an individual edit", r"Plex Warning: Unable to batch \1 update; using individual edits"),
    (r"Filter Error: No (TMDb|TVDb|IMDb) ID found for .+", r"Filter Error: No \1 ID found"),
    (r".*Poster \| No Reset Image Found", "Poster Warning: No Reset Image Found"),
    (r".*Background \| No Reset Image Found", "Background Warning: No Reset Image Found"),
    (r".*Logo \| No Reset Image Found", "Logo Warning: No Reset Image Found"),
    (r".*Square Art \| No Reset Image Found", "Square Art Warning: No Reset Image Found"),
    (r".+ Warning: No Background Found at .+", "Warning: No Background Found"),
    (r".+ Warning: No Logo Found at .+", "Warning: No Logo Found"),
    (r".+ Warning: No Poster Found at .+", "Warning: No Poster Found"),
    (r".+ Warning: No Square Art Found at .+", "Warning: No Square Art Found"),
]


def _convert_message(message):
    summary = message.split(": ", 1)[1].rstrip(":")
    if " for " not in summary:
        return summary
    text, source = summary.rsplit(" for ", 1)
    source = source.replace(" ID", " IDs").replace(" Guid", " Guids")
    return f"{text} for {source}"


def detailed_summary_rules(rating_sources):
    overlay_rules = [
        DetailedSummaryRule("overlay", "No Items found for", r"No Items found for (?P<detail>.+)", "No Items found"),
        *[
            DetailedSummaryRule(
                "overlay",
                f"Overlay Warning: No '{rating_source}' found",
                rf"Overlay Warning: No '{re.escape(rating_source)}' found for (?P<detail>.*)",
                f"No '{rating_source}' found",
            )
            for rating_source in ["audience_rating", "critic_rating", "user_rating", *rating_sources]
        ],
        DetailedSummaryRule("overlay", "Overlay Error: No '", r"Overlay Error: No '(?P<value><<.+>>.*)' found$", "No '{value}' found", detail_group=None),
        DetailedSummaryRule("overlay", "Overlays Attempted on", r"Overlays Attempted on (?P<detail>.*): .+", "Overlays Attempted on"),
    ]
    convert_messages = [
        "Convert Warning: No TVDb ID or IMDb ID found for AniDB ID",
        "Convert Warning: No AniDB ID Found for AniList ID",
        "Convert Warning: No AniDB ID Found for MyAnimeList ID",
        "Convert Warning: No IMDb ID found for TMDb ID",
        "Convert Warning: No TMDb ID found for IMDb ID",
        "Convert Warning: No TVDb ID found for TMDb ID",
        "Convert Warning: No TMDb ID found for TVDb ID",
        "Convert Warning: No IMDb ID found for TVDb ID",
        "Convert Warning: No TVDb ID found for IMDb ID",
        "Convert Warning: No AniDB ID to Convert to MyAnimeList ID for Guid",
        "Convert Error: No AniDB ID found for IMDb ID",
        "Convert Error: No AniDB ID found for TVDb ID",
        "Convert Error: No MyAnimeList ID found for AniDB ID",
        "Convert Error: No AniDB Anime found for AniDB ID",
        "Convert Error: No AniDB ID found for MyAnimeList ID",
        "Convert Error: No mapping found for AniDB ID",
        "Convert Error: No TVDb ID found for TMDb ID",
    ]
    convert_rules = [DetailedSummaryRule("convert", message, rf"{re.escape(message)} '(?P<detail>.*)'", _convert_message(message)) for message in convert_messages]
    return [*overlay_rules, *convert_rules]


def normalize_summary_message(message):
    for pattern, replacement in SUMMARY_NORMALIZATIONS:
        if match := re.match(pattern, message):
            return match.expand(replacement)
    return message


class RunLogSummary:
    def __init__(self, rating_sources, details=False):
        self.details = details
        self.rules = detailed_summary_rules(rating_sources)
        self.sections = defaultdict(lambda: defaultdict(Counter))
        self.severities = defaultdict(Counter)

    def add(self, severity, message):
        for rule_index, rule in enumerate(self.rules):
            if not message.startswith(rule.prefix):
                continue
            if match := re.match(rule.pattern, message):
                label = rule.message.format(**match.groupdict())
                detail = match.groupdict().get(rule.detail_group, "") if rule.detail_group else ""
                self.sections[rule.section][(rule_index, label)][detail] += 1
                return
        normalized = message if self.details else normalize_summary_message(message)
        self.severities[severity][normalized] += 1

    def add_formatted_line(self, line):
        for severity in SEVERITIES:
            if f"[{severity}]" in line:
                message = line.split("|", 1)[1].rsplit("|", 1)[0].strip()
                self.add(severity, message)
                return
        continuation = line.strip().rsplit("|", 1)[0].strip()
        if continuation.startswith("Overlays Attempted on"):
            self.add("ERROR", continuation)

    def has_messages(self):
        return bool(self.sections or self.severities)

    def section_rows(self, section):
        rows = [(rule_index, message, detail_counts) for (rule_index, message), detail_counts in self.sections.get(section, {}).items()]
        for _, message, detail_counts in sorted(rows, key=lambda row: (row[0], -sum(row[2].values()))):
            yield sum(detail_counts.values()), message, [detail for detail in detail_counts if detail]

    def severity_rows(self, severity):
        return self.severities.get(severity, Counter()).most_common()
