---
hide:
  - toc
---
# BoxOfficeMojo Never Hit"

Uses the [Never Hit Lists](https://www.boxofficemojo.com/charts/overall/) (Bottom Section) to collect items.

**Builder Attribute:** `mojo_never`  

**Builder Value:** Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } of Attributes

## Builder Attributes

| Attribute | Description                                                                                                                                   |
|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| `chart`   | Determines the chart you want to use.<br>**Allowed Values:** Item in the dropdown found [here](https://www.boxofficemojo.com/charts/overall/) |
| `never`   | Determines the never filter to use.<br>**Default Value:** `1`<br>**Allowed Values:** `1`, `5`, or `10`                                        |
| `limit`   | The maximum number of results to return.<br>**Default Value:** Returns all results<br>**Allowed Values:** Number greater than 0               |
    
### Example Mojo Never Hit Builder(s)

```yaml
collections:

  "Top 100 Domestic Never #1":
    mojo_never:
      chart: domestic
      limit: 100

  "Top 100 Domestic Never #10":
    mojo_never:
      chart: domestic
      never: 10
      limit: 100

  "Top 100 German Never #1":
    mojo_never:
      chart: germany
      limit: 100
```
