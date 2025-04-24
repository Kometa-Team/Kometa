---
hide:
  - toc
---
# BoxOfficeMojo International
    
Uses the International Box Office to collect items.

**Builder Attribute:** `mojo_international`  

**Builder Value:** Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } of Attributes

## Builder Attributes
    
| Attribute    | Description                                                                                                                                                                          |
|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `range`      | Determines the type of time range of the Box Office.<br>**Allowed Values:** `weekend`, `monthly`, `quarterly`, or `yearly`                                                           |
| `chart`      | Determines the chart you want to use.<br>**Default Value:** `international`<br>**Allowed Values:** Item in the dropdown found [here](https://www.boxofficemojo.com/intl/)            |
| `year`       | Determines the year of the Box Office.<br>**Default Value:** `current`<br>**Allowed Values:** Number between 1977 and the current year, `current`, or relative current (`current-#`) |
| `range_data` | Determines the actual time range of the Box Office. Required for all ranges except `yearly`. Input depends on the `range` selected.                                                  |
| `limit`      | The maximum number of results to return.<br>**Default Value:** Returns all results<br>**Allowed Values:** Number greater than 0                                                      |

## Allowed Values for `range_data`
    
| Range       | Allowed Values                                                                                                |
|-------------|---------------------------------------------------------------------------------------------------------------|
| `weekend`   | Week number (1–53), `current`, or relative (`current-#`) where `#` is days before current                     |
| `monthly`   | `january`, `february`, ..., `december`, `current`, or relative (`current-#`) where `#` is days before current |
| `quarterly` | `q1`, `q2`, `q3`, `q4`, `current`, or relative (`current-#`) where `#` is days before current                 |
    
### Example Mojo International Builder(s)
    
```yaml
collections:

  Current International Box Office:
    mojo_international:
      range: yearly
      year: current

  Last Year's International Box Office:
    mojo_international:
      range: yearly
      year: current-1

  Last Month's Top 10 German Box Office:
    mojo_international:
      range: monthly
      range_data: current
      chart: germany
      year: current-1
      limit: 10
```