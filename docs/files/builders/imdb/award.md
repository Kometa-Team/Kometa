---
hide:
  - toc
---
# IMDb Award

Finds every item in an [IMDb Event](https://www.imdb.com/event/).

| Award Parameter           | Description                                                                                                                                                                                                                                                                                                                 |
|:--------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `event_id`                | Specify the IMDb Event ID to search. **This attribute is required.**<br>**Options:** The ID found in the URLs linked on the [IMDb Events Page](https://www.imdb.com/event/). (ex. `ev0000003`)                                                                                                                              |
| `event_year`<sup>**1**</sup>  | Specify the year of the Event to look at. **This attribute is required.**<br>**Options:** `all`, any year, any negative year (ex. `-10` for 10 years ago), list of years, or year range (ex. `2000-2009`,  `2000-current`, or `-30-current` (Last 30 Years)) from the years under the Event History Sidebar on an Event page. |
| `award_filter`            | Filter by the Award heading. Can only accept multiple values as a list.<br>**Options:** Any Black Award heading on an Event Page.                                                                                                                                                                                           |
| `category_filter`         | Filter by the Category heading. Can only accept multiple values as a list.<br>**Options:** Any Gold/Yellow Category heading on an Event Page.                                                                                                                                                                               |
| `winning`                 | Filter by if the Item Won the award.<br>**Options:** `true`/`false`<br>**Default:** `false`                                                                                                                                                                                                                                 |

???+ example "Example Award and Category Filter"

    In the below example, "Grand Jury Prize" is the award_filter, and "Documentary" is the `category_filter`. You can use both of these filters together.

    ![imdbfilter.png](../../assets/images/files/builders/imdb-award-filters.png)

1. When using multiple years the only available Event IDs are:

```yaml
{%    
  include-markdown "https://raw.githubusercontent.com/Kometa-Team/IMDb-Awards/master/event_ids.yml"
  comments=false
%}
```
### Example IMDb Award Builder(s)

```yaml
collections:
  Academy Award Winners 2023:
    imdb_award: 
      event_id: ev0000003
      event_year: 2023
      winning: true
```
```yaml
collections:
  Academy Award 2023 Best Picture Nominees:
    imdb_award: 
      event_id: ev0000003
      event_year: 2023
      category_filter: Best Motion Picture of the Year
```
