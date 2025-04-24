---
hide:
  - toc
---
# BoxOfficeMojo All Time

Uses the [All Time Lists](https://www.boxofficemojo.com/charts/overall/) to collect items.

**Builder Attribute:** `mojo_all_time`  

**Builder Value:** Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } of Attributes

## Builder Attributes
    
| Attribute               | Description                                                                                                                     |
|-------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| `chart`                 | Determines the chart you want to use.<br>**Allowed Values:** `domestic` or `worldwide`                                          |
| `content_rating_filter` | Determines the content rating chart to use.<br>**Allowed Values:** `g`, `g/pg`, `pg`, `pg-13`, `r`, or `nc-17`                  |
| `limit`                 | The maximum number of results to return.<br>**Default Value:** Returns all results<br>**Allowed Values:** Number greater than 0 |

### Example Mojo All Time Builder(s)
    
```yaml
collections:

  Top 100 Domestic All Time Grosses:
    mojo_all_time:
      chart: domestic
      limit: 100

  Top 100 Worldwide All Time Grosses:
    mojo_all_time:
      chart: worldwide
      limit: 100

  Top 10 Domestic All Time G Movie Grosses:
    mojo_all_time:
      chart: domestic
      content_rating_filter: g
      limit: 10
```
