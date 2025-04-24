---
hide:
  - toc
---
# BoxOfficeMojo Worldwide
    
Uses the [Worldwide Box Office](https://www.boxofficemojo.com/year/world/) to collect items.

**Builder Attribute:** `mojo_world`  

**Builder Value:** Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } of Attributes

## Builder Attributes

| Attribute | Description                                                                                                                                                                                              |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `year`    | The year of the [Worldwide Box Office](https://www.boxofficemojo.com/year/world/) to pull.<br>**Allowed Values:** Number between 1977 and the current year, `current`, or relative current (`current-#`) |
| `limit`   | The maximum number of results to return.<br>**Default Value:** Returns all results<br>**Allowed Values:** Number greater than 0                                                                          |

### Example Mojo Worldwide Builder(s)
    
```yaml
collections:

  Current Worldwide Box Office:
    mojo_world:
      year: current

  Last Year's Worldwide Box Office:
    mojo_world:
      year: current-1

  2020 Top 10 Worldwide Box Office:
    mojo_world:
      year: 2020
      limit: 10
```