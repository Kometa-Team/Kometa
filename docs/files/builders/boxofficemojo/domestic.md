---
hide:
  - toc
---
# BoxOfficeMojo Domestic

Uses the Domestic Box Office to collect items.

**Builder Attribute:** `mojo_domestic`  

**Builder Value:** Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } of Attributes

## Builder Attributes
    
| Attribute    | Description                                                                                                                                                                                                                           |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `range`      | Determines the type of time range of the Box Office.<br>**Allowed Values:** `daily`, `weekend`, `weekly`, `monthly`, `quarterly`, `yearly`, `season`, or `holiday`                                                                    |
| `year`       | Determines the year of the Box Office. This attribute is ignored for the `daily` range.<br>**Default Value:** `current`<br>**Allowed Values:** Number between 1977 and the current year, `current`, or relative current (`current-#`) |
| `range_data` | Determines the actual time range of the Box Office. The input changes depending on the value of `range`.<br>**Required:** Yes, except for `yearly` range                                                                              |
| `limit`      | The maximum number of results to return.<br>**Default Value:** Returns all results<br>**Allowed Values:** Number greater than 0                                                                                                       |

## Allowed Values for `range_data`

| Range       | Allowed Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `daily`     | Date in the format `MM-DD-YYYY`, `current`, or relative (`current-#`) where `#` is days before current                                                                                                                                                                                                                                                                                                                                                                                 |
| `weekend`   | Week number (1–53), `current`, or relative (`current-#`) where `#` is days before current                                                                                                                                                                                                                                                                                                                                                                                              |
| `weekly`    | Week number (1–53), `current`, or relative (`current-#`) where `#` is days before current                                                                                                                                                                                                                                                                                                                                                                                              |
| `monthly`   | `january`, `february`, ..., `december`, `current`, or relative (`current-#`) where `#` is days before current                                                                                                                                                                                                                                                                                                                                                                          |
| `quarterly` | `q1`, `q2`, `q3`, `q4`, `current`, or relative (`current-#`) where `#` is days before current                                                                                                                                                                                                                                                                                                                                                                                          |
| `season`    | `winter`, `spring`, `summer`, `fall`, `holiday`, or `current`                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `holiday`   | `new_years_day`, `new_year_weekend`, `mlk_day`, `mlk_day_weekend`, `presidents_day`, `presidents_day_weekend`, `easter`, `easter_weekend`, `memorial_day`, `memorial_day_weekend`, `independence_day`, `independence_day_weekend`, `labor_day`, `labor_day_weekend`, `indigenous_day`, `indigenous_day_weekend`, `halloween`, `thanksgiving`, `thanksgiving_3`, `thanksgiving_4`, `thanksgiving_5`, `post_thanksgiving_weekend`, `christmas_day`, `christmas_weekend`, `new_years_eve` |
    
### Example Mojo Domestic Builder(s)
    
```yaml
collections:
  Current Domestic Box Office:
    mojo_domestic:
      range: yearly
      year: current

  Last Year's Domestic Box Office:
    mojo_domestic:
      range: yearly
      year: current-1

  Last Month's Top 10 Domestic Box Office:
    mojo_domestic:
      range: monthly
      range_data: current
      year: current-1
      limit: 10
```