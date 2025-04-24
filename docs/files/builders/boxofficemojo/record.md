---
hide:
  - toc
---
# BoxOfficeMojo Other Records

Uses the [Weekend Records](https://www.boxofficemojo.com/charts/weekend/), [Daily Records](https://www.boxofficemojo.com/charts/daily/),
and [Miscellaneous Records](https://www.boxofficemojo.com/charts/misc/) to collect items.

**Builder Attribute:** `mojo_record`

**Builder Value:** Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } of Attributes

## Builder Attributes

| Attribute | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `chart`   | Determines the record you want to use.<br>**Allowed Values:**<br>`second_weekend_drop`, `post_thanksgiving_weekend_drop`, `top_opening_weekend`, `worst_opening_weekend_theater_avg`, `mlk_opening`, `easter_opening`, `memorial_opening`, `labor_opening`, `president_opening`, `thanksgiving_3_opening`, `thanksgiving_5_opening`, `mlk`, `easter`, `4th`, `memorial`, `labor`, `president`, `thanksgiving_3`, `thanksgiving_5`, `january`, `february`, `march`, `april`, `may`, `june`, `july`, `august`, `september`, `october`, `november`, `december`, `spring`, `summer`, `fall`, `holiday_season`, `winter`, `g`, `g/pg`, `pg`, `pg-13`, `r`, `nc-17`, `top_opening_weekend_theater_avg_all`, `top_opening_weekend_theater_avg_wide`, `opening_day`, `single_day_grosses`, `christmas_day_gross`, `new_years_day_gross`, `friday`, `saturday`, `sunday`, `monday`, `tuesday`, `wednesday`, `thursday`, `friday_non_opening`, `saturday_non_opening`, `sunday_non_opening`, `monday_non_opening`, `tuesday_non_opening`, `wednesday_non_opening`, `thursday_non_opening`, `biggest_theater_drop`, `opening_week` |
| `limit`   | The maximum number of results to return.<br>**Default Value:** Returns all results<br>**Allowed Values:** Number greater than 0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |

### Example Mojo Other Records Builder(s)

```yaml
collections:

  Top 10 Biggest Opening Weekends:
    mojo_record:
      chart: top_opening_weekend
      limit: 10

  Top 10 Biggest Opening Day:
    mojo_record:
      chart: opening_day
      limit: 10

  Top 10 Biggest Opening Weeks:
    mojo_record:
      chart: opening_week
      limit: 10
```