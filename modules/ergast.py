from datetime import datetime, timedelta
from modules import util
from modules.util import Failed

logger = util.logger

base_url = "http://ergast.com/api/f1/"

translations = {
    "nl": {
        "70th Anniversary": "70th Anniversary", "Abu Dhabi": "Abu Dhabi", "Argentine": "Argentinië", "Australian": "Australië",
        "Austrian": "Oostenrijk", "Azerbaijan": "Azerbeidzjan", "Bahrain": "Bahrein", "Belgian": "België", "Brazilian": "Brazilië",
        "British": "Groot-Brittannië", "Caesars Palace": "Caesars Palace", "Canadian": "Canada", "Chinese": "China", "Dallas": "Dallas",
        "Detroit": "Detroit", "Dutch": "Nederland", "Eifel": "Eifel", "Emilia Romagna": "Emilia Romagna", "European": "Europa",
        "French": "Frankrijk", "German": "Duitsland", "Hungarian": "Hongarije", "Indian": "India", "Indianapolis 500": "Indianapolis 500",
        "Italian": "Italië", "Japanese": "Japan", "Korean": "Zuid-Korea", "Luxembourg": "Luxemburg", "Malaysian": "Maleisië",
        "Mexican": "Mexico", "Mexico City": "Mexico City", "Miami": "Miami", "Monaco": "Monaco", "Moroccan": "Marroko",
        "Pacific": "Pacific", "Pescara": "Pescara", "Portuguese": "Portugal", "Qatar": "Qatar", "Russian": "Rusland",
        "Sakhir": "Sakhir", "San Marino": "San Marino", "Saudi Arabian": "Saudi Arabië", "Singapore": "Singapore",
        "South African": "Zuid-Afrika", "Spanish": "Spanje", "Styrian": "Stiermarken", "Swedish": "Zweden", "Swiss": "Zwitserland",
        "São Paulo": "São Paulo", "Turkish": "Turkije", "Tuscan": "Toscane", "United States": "Verenigde Staten"
    }
}

terms = {
    "free practice 1": ["free practice 1", "vrije training 1", "fp1", "vt1"],
    "free practice 2": ["free practice 2", "vrije training 2", "fp2", "vt2"],
    "free practice 3": ["free practice 3", "vrije training 3", "fp3", "vt3"],
    "pre": ["pre", "voorbeschouwing"],
    "post": ["post", "nabeschouwing"],
    "quali": ["quali", "kwalificatie"],
    "shootout": ["shootout"],
    "notebook": ["notebook", "notitieboekje"],
    "preview": ["preview", "seizoensvoorbeschouwing"],
    "summary": ["summary", "samenvatting"],
    "highlight": ["highlight", "hoogtepunten"],
}

names = {
    "nl": {
        "Formula 1 Cafe": "Formule 1 Cafe",
        "Free Practice 1": "Vrije Training 1",
        "Free Practice 2": "Vrije Training 2",
        "Free Practice 3": "Vrije Training 3",
        "Pre-Sprint Race Build-up": "Sprint Race Voorbeschouwing",
        "Post-Sprint Race Analysis": "Sprint Race Nabeschouwing",
        "Sprint Race Session": "Sprint Race",
        "Ted's Sprint Notebook": "Ted's Sprint Notitieboekje",
        "Pre-Qualifying Build-up": "Kwalificatie Voorbeschouwing",
        "Post-Qualifying Analysis": "Kwalificatie Nabeschouwing",
        "Qualifying Session": "Kwalificatie",
        "Season Preview": "Seizoensvoorbeschouwing",
        "Pre-Race Buildup": "Voorbeschouwing",
        "Post-Race Analysis": "Nabeschouwing",
        "Live from the Grid": "Vanaf de grid",
        "Highlights": "Samenvatting",
        "Race Session": "Race",
        "Ted's Race Notebook": "Ted's Race Notitieboekje",
        "Ted's Qualifying Notebook": "Ted's Kwalificatie Notitieboekje",
        "Pre-Sprint Shootout Build-up": "Sprint Shootout Voorbeschouwing",
        "Post-Sprint Shootout Analysis": "Sprint Shootout Nabeschouwing",
        "Sprint Shootout Session": "Sprint Shootout",
    }
}

class Race:
    def __init__(self, data, language):
        self._data = data
        self._language = language
        self.season = util.check_num(self._data["season"], is_int=True)
        self.round = util.check_num(self._data["round"], is_int=True)
        self.name = self._data["raceName"]
        try:
            self.date = datetime.strptime(self._data["date"], "%Y-%m-%d")
        except (ValueError, TypeError):
            self.date = None

    def __str__(self):
        return f"Season {self.season} Round {self.round}: {self.name}"

    def format_name(self, round_prefix, shorten_gp):
        if self._language:
            output = f"GP {self.name.replace(' Grand Prix', '')}" if shorten_gp else self.name
            for eng_value, trans_value in translations[self._language].items():
                output = output.replace(eng_value, trans_value)
        else:
            output = self.name.replace("Grand Prix", "GP") if shorten_gp else self.name
        if round_prefix:
            output = f"{self.round:02} - {output}"
        return output

    def session_info(self, title, sprint_weekend):
        title = title.lower()
        if "cafe" in title:
            output = "Formula 1 Cafe"
        elif any([x in title for x in terms["free practice 1"]]):
            output = "Free Practice 1"
        elif any([x in title for x in terms["free practice 2"]]):
            output = "Free Practice 2"
        elif any([x in title for x in terms["free practice 3"]]):
            output = "Free Practice 3"
        elif "shootout" in title:
            if any([x in title for x in terms["pre"]]):
                output = "Pre-Sprint Shootout Build-up"
            elif any([x in title for x in terms["post"]]):
                output = "Post-Sprint Shootout Analysis"
            else:
                output = "Sprint Shootout Session"
        elif "sprint" in title:
            if any([x in title for x in terms["pre"]]):
                output = "Pre-Sprint Race Build-up"
            elif any([x in title for x in terms["post"]]):
                output = "Post-Sprint Race Analysis"
            elif any([x in title for x in terms["notebook"]]):
                output = "Ted's Sprint Notebook"
            else:
                output = "Sprint Race Session"
        elif any([x in title for x in terms["quali"]]):
            if any([x in title for x in terms["pre"]]):
                output = "Pre-Qualifying Build-up"
            elif any([x in title for x in terms["post"]]):
                output = "Post-Qualifying Analysis"
            elif any ([x in title for x in terms["notebook"]]):
                output = "Ted's Qualifying Notebook"
            else:
                output = "Qualifying Session"
        elif any([x in title for x in terms["preview"]]):
            output = "Season Preview"
        elif any([x in title for x in terms["pre"]]):
            output = "Pre-Race Buildup"
        elif any([x in title for x in terms["post"]]):
            output = "Post-Race Analysis"
        elif "grid" in title:
            output = "Live from the Grid"
        elif any([x in title for x in terms["summary"] + terms["highlight"]]):
            output = "Highlights"
        elif any([x in title for x in terms["notebook"]]):
            output = "Ted's Race Notebook"
        else:
            output = "Race Session"
        if "2160" in title or "4K" in title:
            output = f"{output} (4K)"

        if (sprint_weekend and any([x in output for x in ["Sprint", "Free Practice 2"]])) or \
                (not sprint_weekend and any([x in output for x in ["Qualifying", "Free Practice 3"]])):
            video_date = self.date - timedelta(days=1)
        elif (sprint_weekend and any([x in output for x in ["Qualifying", "Free Practice 1", "Formula 1 Cafe"]])) or \
                (not sprint_weekend and any([x in output for x in ["Free Practice 1", "Free Practice 2", "Formula 1 Cafe"]])):
            video_date = self.date - timedelta(days=2)
        else:
            video_date = self.date

        if self._language and self._language in names and output in names[self._language]:
            output = names[self._language][output]
        return output, video_date


class Ergast:
    def __init__(self, requests, cache):
        self.requests = requests
        self.cache = cache

    def get_races(self, year, language, ignore_cache=False):
        expired = None
        if self.cache and not ignore_cache:
            race_list, expired = self.cache.query_ergast(year, self.cache.expiration)
            if race_list and expired is False:
                return [Race(r, language) for r in race_list]
        response = self.requests.get(f"{base_url}{year}.json")
        if response.status_code < 400:
            races = [Race(r, language) for r in response.json()["MRData"]["RaceTable"]["Races"]]
            if self.cache and not ignore_cache:
                self.cache.update_ergast(expired, year, races, self.cache.expiration)
            return races
        else:
            raise Failed(f"Ergast Error: F1 Season: {year} Not found")
