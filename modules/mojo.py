from datetime import datetime
from modules import util
from modules.request import parse_qs, urlparse
from modules.util import Failed
from num2words import num2words

logger = util.logger

builders = ["mojo_world", "mojo_domestic", "mojo_international", "mojo_record", "mojo_all_time", "mojo_never"]
top_options = {
    "second_weekend_drop": ("Biggest Second Weekend Drops", "/chart/biggest_second_weekend_gross_drop/", None),
    "post_thanksgiving_weekend_drop": ("Largest Post-Thanksgiving Weekend Drops", "/chart/post_thanksgiving_weekend_drop/", None),
    "top_opening_weekend": ("Top Opening Weekends", "/chart/top_opening_weekend/", None),
    "worst_opening_weekend_theater_avg": ("Worst Opening Weekend Per-Theater Averages", "/chart/btm_wide_opening_weekend_theater_avg/", None),
    "top_opening_weekend_theater_avg_all": ("Top Opening Theater Averages", "/chart/top_opening_weekend_theater_avg/", {"by_release_scale": "all"}),
    "top_opening_weekend_theater_avg_wide": ("Top Wide Opening Theater Averages", "/chart/top_opening_weekend_theater_avg/", {"by_release_scale": "wide"}),
    "january": ("Top Opening Weekend in January", "/chart/release_top_opn_wkd_in_month/", {"in_occasion": "january"}),
    "february": ("Top Opening Weekend in February", "/chart/release_top_opn_wkd_in_month/", {"in_occasion": "february"}),
    "march": ("Top Opening Weekend in March", "/chart/release_top_opn_wkd_in_month/", {"in_occasion": "march"}),
    "april": ("Top Opening Weekend in April", "/chart/release_top_opn_wkd_in_month/", {"in_occasion": "april"}),
    "may": ("Top Opening Weekend in May", "/chart/release_top_opn_wkd_in_month/", {"in_occasion": "may"}),
    "june": ("Top Opening Weekend in June", "/chart/release_top_opn_wkd_in_month/", {"in_occasion": "june"}),
    "july": ("Top Opening Weekend in July", "/chart/release_top_opn_wkd_in_month/", {"in_occasion": "july"}),
    "august": ("Top Opening Weekend in August", "/chart/release_top_opn_wkd_in_month/", {"in_occasion": "august"}),
    "september": ("Top Opening Weekend in September", "/chart/release_top_opn_wkd_in_month/", {"in_occasion": "september"}),
    "october": ("Top Opening Weekend in October", "/chart/release_top_opn_wkd_in_month/", {"in_occasion": "october"}),
    "november": ("Top Opening Weekend in November", "/chart/release_top_opn_wkd_in_month/", {"in_occasion": "november"}),
    "december": ("Top Opening Weekend in December", "/chart/release_top_opn_wkd_in_month/", {"in_occasion": "december"}),
    "spring": ("Top Opening Weekend in Spring", "/chart/release_top_opn_wkd_in_season/", {"in_occasion": "spring"}),
    "summer": ("Top Opening Weekend in Summer", "/chart/release_top_opn_wkd_in_season/", {"in_occasion": "summer"}),
    "fall": ("Top Opening Weekend in Fall", "/chart/release_top_opn_wkd_in_season/", {"in_occasion": "fall"}),
    "holiday_season": ("Top Opening Weekend in The Holiday Season", "/chart/release_top_opn_wkd_in_season/", {"in_occasion": "holiday_season"}),
    "winter": ("Top Opening Weekend in Winter", "/chart/release_top_opn_wkd_in_season/", {"in_occasion": "winter"}),
    "g": ("Top Opening Weekend for G Ratings", "/chart/top_opening_wknd_by_mpaa/", {"by_mpaa": "G"}),
    "g/pg": ("Top Opening Weekend for G/PG Ratings", "/chart/top_opening_wknd_by_mpaa/", {"by_mpaa": "G%2FPG"}),
    "pg": ("Top Opening Weekend for PG Ratings", "/chart/top_opening_wknd_by_mpaa/", {"by_mpaa": "PG"}),
    "pg-13": ("Top Opening Weekend for PG-13 Ratings", "/chart/top_opening_wknd_by_mpaa/", {"by_mpaa": "PG-13"}),
    "r": ("Top Opening Weekend for R Ratings", "/chart/top_opening_wknd_by_mpaa/", {"by_mpaa": "R"}),
    "nc-17": ("Top Opening Weekend for NC-17 Ratings", "/chart/top_opening_wknd_by_mpaa/", {"by_mpaa": "NC-17"}),
    "mlk": ("Top Weekend for MLK Day", "/chart/release_top_weekend_gross/", {"by_occasion", "us_mlkday_weekend"}),
    "easter": ("Top Weekend for Easter", "/chart/release_top_weekend_gross/", {"by_occasion", "easter_weekend"}),
    "4th": ("Top Weekend for the 4th of July", "/chart/release_top_weekend_gross/", {"by_occasion", "us_july4_weekend"}),
    "memorial": ("Top Weekend for Memorial Day", "/chart/release_top_weekend_gross/", {"by_occasion", "us_memorialday_weekend"}),
    "labor": ("Top Weekend for Labor Day", "/chart/release_top_weekend_gross/", {"by_occasion", "us_laborday_weekend"}),
    "president": ("Top Weekend for President's Day", "/chart/release_top_weekend_gross/", {"by_occasion", "us_presidentsday_weekend"}),
    "thanksgiving_3": ("Top 3 Day Weekend for Thanksgiving", "/chart/release_top_weekend_gross/", {"by_occasion", "us_thanksgiving_3"}),
    "thanksgiving_5": ("Top 5 Day Weekend for Thanksgiving", "/chart/release_top_weekend_gross/", {"by_occasion", "us_thanksgiving_5"}),
    "mlk_opening": ("Top Opening Weekend for MLK Day", "/chart/top_opening_holiday_weekends/", {"by_occasion", "us_mlkday_weekend"}),
    "easter_opening": ("Top Opening Weekend for Easter", "/chart/top_opening_holiday_weekends/", {"by_occasion", "easter_weekend"}),
    "memorial_opening": ("Top Opening Weekend for Memorial Day", "/chart/top_opening_holiday_weekends/", {"by_occasion", "us_memorialday_weekend"}),
    "labor_opening": ("Top Opening Weekend for Labor Day", "/chart/top_opening_holiday_weekends/", {"by_occasion", "us_laborday_weekend"}),
    "president_opening": ("Top Opening Weekend for MLK Day", "/chart/top_opening_holiday_weekends/", {"by_occasion", "us_presidentsday_weekend"}),
    "thanksgiving_3_opening": ("Top 3 Day Opening Weekend for Thanksgiving", "/chart/top_thanksgiving_openings/", {"by_occasion", "us_thanksgiving_3"}),
    "thanksgiving_5_opening": ("Top 5 Day Opening Weekend for Thanksgiving", "/chart/top_thanksgiving_openings/", {"by_occasion", "us_thanksgiving_5"}),
    "opening_week": ("Top Opening Week", "/chart/top_opening_week/", None),
    "biggest_theater_drop": ("Biggest Theater Drops", "/chart/biggest_third_weekend_num_theaters_drop/", None),
    "opening_day": ("Top Opening Day", "/chart/top_opening_day/", None),
    "single_day_grosses": ("Top Day", "/chart/release_top_daily_gross/", None),
    "christmas_day_gross": ("Top Christmas Day", "/chart/release_top_holiday_gross/", {"by_occasion": "christmas_day"}),
    "new_years_day_gross": ("Top New Years Day", "/chart/release_top_holiday_gross/", {"by_occasion": "newyearsday"}),
    "friday": ("Top Friday", "/chart/release_top_daily_gross_by_dow/", {"by_occasion": "friday"}),
    "saturday": ("Top Saturday", "/chart/release_top_daily_gross_by_dow/", {"by_occasion": "saturday"}),
    "sunday": ("Top Sunday", "/chart/release_top_daily_gross_by_dow/", {"by_occasion": "sunday"}),
    "monday": ("Top Monday", "/chart/release_top_daily_gross_by_dow/", {"by_occasion": "monday"}),
    "tuesday": ("Top Tuesday", "/chart/release_top_daily_gross_by_dow/", {"by_occasion": "tuesday"}),
    "wednesday": ("Top Wednesday", "/chart/release_top_daily_gross_by_dow/", {"by_occasion": "wednesday"}),
    "thursday": ("Top Thursday", "/chart/release_top_daily_gross_by_dow/", {"by_occasion": "thursday"}),
    "friday_non_opening": ("Top Friday Non-Opening", "/chart/top_non_opening_by_dow/", {"by_occasion": "friday"}),
    "saturday_non_opening": ("Top Saturday Non-Opening", "/chart/top_non_opening_by_dow/", {"by_occasion": "saturday"}),
    "sunday_non_opening": ("Top Sunday Non-Opening", "/chart/top_non_opening_by_dow/", {"by_occasion": "sunday"}),
    "monday_non_opening": ("Top Monday Non-Opening", "/chart/top_non_opening_by_dow/", {"by_occasion": "monday"}),
    "tuesday_non_opening": ("Top Tuesday Non-Opening", "/chart/top_non_opening_by_dow/", {"by_occasion": "tuesday"}),
    "wednesday_non_opening": ("Top Wednesday Non-Opening", "/chart/top_non_opening_by_dow/", {"by_occasion": "wednesday"}),
    "thursday_non_opening": ("Top Thursday Non-Opening", "/chart/top_non_opening_by_dow/", {"by_occasion": "thursday"}),
}
chart_options = ["domestic", "worldwide"]
content_rating_options = {
    "g": "G",
    "g/pg": "G%2FPG",
    "pg": "PG",
    "pg-13": "PG-13",
    "r": "R",
    "nc-17": "NC-17",
}
never_in_options = {
    "1": ("#1", "never_1"),
    "5": ("the Top 5", "never_5"),
    "10": ("the Top 10", "never_10"),
}
intl_range_options = ["weekend", "monthly", "quarterly", "yearly"]
dome_range_options = intl_range_options + ["daily", "weekly", "season", "holiday"]
year_options = ["current"] + [str(t) for t in range(1977, datetime.now().year + 1)]
quarter_options = ["current", "q1", "q2", "q3", "q4"]
quarters = {1: "q1", 2: "q1", 3: "q1", 4: "q2", 5: "q2", 6: "q2", 7: "q3", 8: "q3", 9: "q3", 10: "q4", 11: "q4", 12: "q4"}
season_options = ["current", "winter", "spring", "summer", "fall", "holiday"]
seasons = {1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "summer", 6: "summer", 7: "summer", 8: "summer", 9: "fall", 10: "fall", 11: "holiday", 12: "holiday"}
holiday_options = {
    "new_years_day": ("New Year's Day", "newyearsday"),
    "new_year_weekend": ("New Year Weekend", "us_newyear_weekend"),
    "mlk_day": ("MLK Day", "us_mlkday"),
    "mlk_day_weekend": ("MLK Day Weekend", "us_mlkday_weekend"),
    "presidents_day": ("President's Day", "us_presidentsday"),
    "presidents_day_weekend": ("President's Day Weekend", "us_presidentsday_weekend"),
    "easter": ("Easter", "easter_sunday"),
    "easter_weekend": ("Easter Weekend", "easter_weekend"),
    "memorial_day": ("Memorial Day", "us_memorialday"),
    "memorial_day_weekend": ("Memorial Day Weekend", "us_memorialday_weekend"),
    "independence_day": ("Independence Day", "us_july4"),
    "independence_day_weekend": ("Independence Day Weekend", "us_july4_weekend"),
    "labor_day": ("Labor Day", "us_laborday"),
    "labor_day_weekend": ("Labor Day Weekend", "us_laborday_weekend"),
    "indigenous_day": ("Indigenous People's Day", "us_indig_peoples_day"),
    "indigenous_day_weekend": ("", "us_indig_peoples_day_weekend"),
    "halloween": ("Halloween", "halloween"),
    "thanksgiving": ("Thanksgiving", "us_thanksgiving"),
    "thanksgiving_3": ("Thanksgiving Weekend", "us_thanksgiving_3"),
    "thanksgiving_4": ("Thanksgiving 4-Day Weekend", "us_thanksgiving_4"),
    "thanksgiving_5": ("Thanksgiving 5-Day Weekend", "us_thanksgiving_5"),
    "post_thanksgiving_weekend": ("Post-Thanksgiving Weekend", "us_post_thanksgiving_weekend"),
    "christmas_day": ("Christmas Day", "christmas_day"),
    "christmas_weekend": ("Christmas Weekend", "us_christmas_weekend"),
    "new_years_eve": ("New Year's Eve", "newyearseve")
}
base_url = "https://www.boxofficemojo.com"


class BoxOfficeMojo:
    def __init__(self, requests, cache):
        self.requests = requests
        self.cache = cache
        self._never_options = None
        self._intl_options = None
        self._year_options = None

    def _options(self, url, nav_type="area"):
        output = {}
        options = self._request(url, xpath=f"//select[@id='{nav_type}-navSelector']/option")
        for option in options:
            query = parse_qs(urlparse(option.xpath("@value")[0]).query)
            output[option.xpath("text()")[0].lower()] = query["area"][0] if "area" in query else ""
        return output

    @property
    def never_options(self):
        if self._never_options is None:
            self._never_options = self._options("/chart/never_in_top/")
        return self._never_options

    @property
    def intl_options(self):
        if self._intl_options is None:
            self._intl_options = self._options("/intl/")
        return self._intl_options

    @property
    def year_options(self):
        if self._year_options is None:
            self._year_options = [y for y in self._options("/year/world/", nav_type="year")]
        return self._year_options

    def _request(self, url, xpath=None, params=None):
        logger.trace(f"URL: {base_url}{url}")
        if params:
            logger.trace(f"Params: {params}")
        response = self.requests.get_html(f"{base_url}{url}", header=True, params=params)
        return response.xpath(xpath) if xpath else response

    def _parse_list(self, url, params, limit):
        response = self._request(url, params=params)
        total_html = response.xpath("//li[contains(@class, 'mojo-pagination-button-center')]/a/text()")
        total = int(total_html[0].replace(",", "").split(" ")[2]) if total_html else 0
        if total and (limit < 1 or total < limit):
            limit = total
        pages = int((limit - 1) / 200) + 1 if total else 0
        for field_name in ["release ", "title", "release_group"]:
            output = response.xpath(f"//td[contains(@class, 'mojo-field-type-{field_name}')]/a/@href")
            if output:
                break
        for i in range(1, pages):
            response = self._request(url, params={"offset": 200 * i})
            output.extend(response.xpath(f"//td[contains(@class, 'mojo-field-type-{field_name}')]/a/@href"))
        if not limit or len(output) < limit:
            limit = len(output)
        return [i[:i.index("?")] for i in output[:limit]]

    def _imdb(self, url):
        response = self._request(url)
        imdb_url = response.xpath("//select[@id='releasegroup-picker-navSelector']/option[text()='All Releases']/@value")
        if not imdb_url:
            raise Failed(f"Mojo Error: IMDb ID not found at {base_url}{url}")
        return imdb_url[0][7:-1]

    def get_imdb_ids(self, method, data):
        params = None
        if method == "mojo_record":
            text, url, params = top_options[data["chart"]]
        elif method == "mojo_world":
            text = f"{data['year']} Worldwide Box Office"
            url = f"/year/world/{data['year']}/"
        elif method == "mojo_all_time":
            text = f"Top Lifetime {data['chart'].capitalize()}"
            if data["content_rating_filter"] is None:
                url = "/chart/top_lifetime_gross/" if data["chart"] == "domestic" else "/chart/ww_top_lifetime_gross/"
            else:
                text += f" {data['content_rating_filter'].upper()}"
                url = f"/chart/mpaa_title_lifetime_gross/"
                params = {"by_mpaa": content_rating_options[data['content_rating_filter']]}
            text += " Grosses"
        elif method == "mojo_never":
            pretty, arg_key = never_in_options[data["never"]]
            text = f"Top-Grossing Movies That Never Hit {pretty} {data['chart'].capitalize()}"
            url = f"/chart/never_in_top/"
            params = {"by_rank_threshold": data["never"]}
            if data["chart"] != "domestic":
                params["area"] = self.never_options[data["chart"]]
        else:
            chart = data["chart"].capitalize() if "chart" in data else "Domestic"

            if data["range"] == "daily":
                day = datetime.strptime(data["range_data"], "%Y-%m-%d")
                day = day.strftime("%b {th}, %Y").replace("{th}", num2words(day.day, to='ordinal_num'))
                chart_title = f"{day}"
                url = f"/date/{data['range_data']}/"
            elif data["range"] == "weekend":
                chart_title = f"Weekend {data['range_data']} {data['year']}"
                url = f"/weekend/{data['year']}W{data['range_data']:02}/"
            elif data["range"] == "weekly":
                chart_title = f"Week {data['range_data']} {data['year']}"
                url = f"/weekly/{data['year']}W{data['range_data']:02}/"
            elif data["range"] == "monthly":
                chart_title = f"{data['range_data'].capitalize()} {data['year']}"
                url = f"/month/{data['range_data']}/{data['year']}/"
            elif data["range"] == "quarterly":
                chart_title = f"{data['range_data'].capitalize()} {data['year']}"
                url = f"/quarter/{data['range_data']}/{data['year']}/"
            elif data["range"] == "season":
                chart_title = f"{data['range_data'].capitalize()} {data['year']}"
                url = f"/season/{data['range_data']}/{data['year']}/"
            elif data["range"] == "holiday":
                title, slug = holiday_options[data["range_data"]]
                chart_title = f"{title} {data['year']}"
                url = f"/holiday/{slug}/{data['year']}/"
            else:
                chart_title = f"{data['year']}"
                url = f"/year/{data['year']}/"
            text = f"{chart} Box Office For {chart_title}"
        if data["limit"]:
            text += f" ({data['limit']})"
        logger.info(f"Processing {method.replace('_', ' ').title()}: {text}")
        items = self._parse_list(url, params, data["limit"])
        if not items:
            raise Failed(f"Mojo Error: No List Items found in {method}: {data}")
        ids = []
        total_items = len(items)
        for i, item in enumerate(items, 1):
            logger.ghost(f"Finding IMDb ID {i}/{total_items}")
            if "title" in item:
                imdb_id = item[7:-1]
            else:
                imdb_id = None
                expired = None
                if self.cache:
                    imdb_id, expired = self.cache.query_letterboxd_map(item)
                if not imdb_id or expired is not False:
                    try:
                        imdb_id = self._imdb(item)
                    except Failed as e:
                        logger.error(e)
                        continue
                    if self.cache:
                        self.cache.update_letterboxd_map(expired, item, imdb_id)
            ids.append((imdb_id, "imdb"))
        logger.info(f"Processed {total_items} IMDb IDs")
        return ids
