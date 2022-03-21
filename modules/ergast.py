from datetime import datetime, timedelta
from modules import util
from modules.util import Failed

logger = util.logger

base_url = "http://ergast.com/api/f1/"

class Race:
    def __init__(self, data):
        self._data = data
        self.season = util.check_num(self._data["season"], is_int=True)
        self.round = util.check_num(self._data["round"], is_int=True)
        self.name = self._data["raceName"]
        try:
            self.date = datetime.strptime(self._data["date"], "%Y-%m-%d")
        except (ValueError, TypeError):
            self.date = None

    def format_name(self, round_prefix, shorten_gp):
        output = f"{self.round:02} - {self.name}" if round_prefix else self.name
        return output.replace("Grand Prix", "GP") if shorten_gp else output

    def session_info(self, title, sprint_weekend):
        title = title.lower()
        if "fp1" in title or "free practice 1" in title:
            output = "Free Practice 1"
        elif "fp2" in title or "free practice 2" in title:
            output = "Free Practice 2"
        elif "fp3" in title or "free practice 3" in title:
            output = "Free Practice 3"
        elif "sprint" in title and "pre" in title:
            output = "Pre-Sprint Build-up"
        elif "sprint" in title and "post" in title:
            output = "Post-Sprint Analysis"
        elif "sprint" in title:
            output = "Sprint Qualifying"
        elif "quali" in title and "pre" in title:
            output = "Pre-Qualifying Build-up"
        elif "quali" in title and "post" in title:
            output = "Post-Qualifying Analysis"
        elif "quali" in title:
            output = "Qualifying Session"
        elif "summary" in title or "highlight" in title:
            output = "Highlights"
        else:
            output = "Race Session"
        if "2160" in title or "4K" in title:
            output = f"{output} (4K)"

        if (sprint_weekend and ("Sprint" in output or "Free Practice 2" in output)) or \
                (not sprint_weekend and ("Qualifying" in output or "Free Practice 3" in output)):
            return output, self.date - timedelta(days=1)
        elif (sprint_weekend and ("Qualifying" in output or "Free Practice 1" in output)) or \
                (not sprint_weekend and ("Free Practice 1" in output or "Free Practice 2" in output)):
            return output, self.date - timedelta(days=2)
        else:
            return output, self.date

class Ergast:
    def __init__(self, config):
        self.config = config

    def get_races(self, year, ignore_cache=False):
        expired = None
        if self.config.Cache and not ignore_cache:
            race_list, expired = self.config.Cache.query_ergast(year, self.config.Cache.expiration)
            if race_list and expired is False:
                return [Race(r) for r in race_list]
        response = self.config.get(f"{base_url}{year}.json")
        if response.status_code < 400:
            races = [Race(r) for r in response.json()["MRData"]["RaceTable"]["Races"]]
            if self.config.Cache and not ignore_cache:
                self.config.Cache.update_ergast(expired, year, races, self.config.Cache.expiration)
            return races
        else:
            raise Failed(f"Ergast Error: F1 Season: {year} Not found")
