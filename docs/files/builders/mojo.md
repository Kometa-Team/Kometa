# BoxOfficeMojo Builders

You can find items using the lists on [boxofficemojo.com](https://www.boxofficemojo.com/) (BoxOfficeMojo). 

No configuration is required for these builders.

??? blank "`mojo_domestic` - Uses the Domestic Box Office.<a class="headerlink" href="#mojo-domestic" title="Permanent link">¶</a>"

    <div id="mojo-domestic" />Uses the Domestic Box Office to collection items.

    <hr style="margin: 0px;">

    **Works With:** Movies, Playlists, and Custom Sort
    
    **Builder Attribute:** `mojo_domestic`

    **Builder Value:** [Dictionary](../../pmm/yaml.md#dictionaries) of Attributes

    ??? blank "`range` - Determines the type of time range of the Box Office"
        
        Determines the type of the time range of the Box Office.

        **Allowed Values:** `daily`, `weekend`, `weekly`, `monthly`, `quarterly`, `yearly`, `season`, or `holiday`

    ??? blank "`year` - Determines the year of the Box Office"
        
        Determines the year of the Box Office. This attribute is ignored for the `daily` range.

        **Default Value:** `current`

        **Allowed Values:** Number between 1977 and the current year, `current`, or relative current (`current-#`; where
        `#` is the number of year before the current)

    ??? blank "`range_data` - Determines the actual time range of the Box Office"
        
        Determines the actual time range of the Box Office. The input for this value changes depending on the value
        of `range`. 

        ??? warning
    
            This attribute is required for all ranges except the `yearly` range.

        **Daily Allowed Values:** Date in the format `MM-DD-YYYY`, `current`, or relative current (`current-#`; where
        `#` is the number of days before the current)

        **Weekend Allowed Values:** Week Number between 1-53, `current`, or relative current (`current-#`; where `#` 
        is the number of days before the current)

        **Weekly Allowed Values:** Week Number between 1-53, `current`, or relative current (`current-#`; where `#` 
        is the number of days before the current)
    
        **Monthly Allowed Values:** `january`, `february`, `march`, `april`, `may`, `june`, `july`, `august`, 
        `september`, `october`, `november`, `december`, `current`, or relative current (`current-#`; where `#` is the 
        number of days before the current)

        **Quarterly Allowed Values:** `q1`, `q2`, `q3`, `q4`, `current`, or relative current (`current-#`; where `#` 
        is the number of days before the current)

        **Season Allowed Values:** `winter`, `spring`, `summer`, `fall`, `holiday`, or `current`

        **Holiday Allowed Values:** `new_years_day`, `new_year_weekend`, `mlk_day`, `mlk_day_weekend`, 
        `presidents_day`, `presidents_day_weekend`, `easter`, `easter_weekend`, `memorial_day`, `memorial_day_weekend`, 
        `independence_day`, `independence_day_weekend`, `labor_day`, `labor_day_weekend`, `indigenous_day`, 
        `indigenous_day_weekend`, `halloween`, `thanksgiving`, `thanksgiving_3`, `thanksgiving_4`, `thanksgiving_5`, 
        `post_thanksgiving_weekend`, `christmas_day`, `christmas_weekend`, or `new_years_eve`

    ??? blank "`limit` - The maximum number of result to return"
        
        This determines the maximum number of results to return. If there are less results then the limit then all will 
        be returned. 

        **Default Value:** Returns all results

        **Allowed Values:** Number greter than 0

    ???+ example "Example"
        
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
              
          Last Months Top 10 Domestic Box Office:
            mojo_domestic:
              range: monthly
              range_data: current
              year: current-1
              limit: 10
        ```

??? blank "`mojo_international` - Uses the International Box Office.<a class="headerlink" href="#mojo-international" title="Permanent link">¶</a>"

    <div id="mojo-international" />Uses the International Box Office to collection items.

    <hr style="margin: 0px;">

    **Works With:** Movies, Playlists, and Custom Sort
    
    **Builder Attribute:** `mojo_international`

    **Builder Value:** [Dictionary](../../pmm/yaml.md#dictionaries) of Attributes

    ??? blank "`range` - Determines the type of time range of the Box Office"
        
        Determines the type of the time range of the Box Office.

        **Allowed Values:** `weekend`,  `monthly`, `quarterly`, or `yearly`

    ??? blank "`chart` - Determines the chart you want to use"

        Determines the chart you want to use.

        **Default Value:** `international`

        **Allowed Values:** Item in the drop down found [here](https://www.boxofficemojo.com/intl/)

    ??? blank "`year` - Determines the year of the Box Office"
        
        Determines the year of the Box Office.

        **Default Value:** `current`

        **Allowed Values:** Number between 1977 and the current year, `current`, or relative current (`current-#`; where
        `#` is the number of year before the current)

    ??? blank "`range_data` - Determines the actual time range of the Box Office"
        
        Determines the actual time range of the Box Office. The input for this value changes depending on the value
        of `range`. 

        ??? warning

            This attribute is required for all ranges except the `yearly` range.

        **Weekend Allowed Values:** Week Number between 1-53, `current`, or relative current (`current-#`; where `#` 
        is the number of days before the current)

        **Monthly Allowed Values:** `january`, `february`, `march`, `april`, `may`, `june`, `july`, `august`, 
        `september`, `october`, `november`, `december`, `current`, or relative current (`current-#`; where `#` is the 
        number of days before the current)

        **Quarterly Allowed Values:** `q1`, `q2`, `q3`, `q4`, `current`, or relative current (`current-#`; where `#` 
        is the number of days before the current)

    ??? blank "`limit` - The maximum number of result to return"
        
        This determines the maximum number of results to return. If there are less results then the limit then all will 
        be returned. 

        **Default Value:** Returns all results

        **Allowed Values:** Number greter than 0

    ???+ example "Example"
        
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
              
          Last Months Top 10 German Box Office:
            mojo_international:
              range: monthly
              range_data: current
              chart: germany
              year: current-1
              limit: 10
        ```

??? blank "`mojo_world` - Uses the Worldwide Box Office.<a class="headerlink" href="#mojo-world" title="Permanent link">¶</a>"

    <div id="mojo-world" />Uses the [Worldwide Box Office](https://www.boxofficemojo.com/year/world/) to collection items.

    <hr style="margin: 0px;">

    **Works With:** Movies, Playlists, and Custom Sort
    
    **Builder Attribute:** `mojo_world`

    **Builder Value:** [Dictionary](../../pmm/yaml.md#dictionaries) of Attributes

    ??? blank "`year` - The year of the Worldwide Box Office"
        
        This determines the year of the [Worldwide Box Office](https://www.boxofficemojo.com/year/world/) to pull.

        **Allowed Values:** Number between 1977 and the current year, `current`, or relative current (`current-#`; where
        `#` is the number of year before the current)

    ??? blank "`limit` - The maximum number of result to return"
        
        This determines the maximum number of results to return. If there are less results then the limit then all will 
        be returned. 

        **Default Value:** Returns all results

        **Allowed Values:** Number greter than 0

    ???+ example "Example"
        
        ```yaml
        collections:

          Current Worlwide Box Office:
            mojo_world:
              year: current
              
          Last Year's Worlwide Box Office:
            mojo_world:
              year: current-1
              
          2020 Top 10 Worlwide Box Office:
            mojo_world:
              year: 2020
              limit: 10
        ```

??? blank "`mojo_all_time` - Uses the All Time Lists.<a class="headerlink" href="#mojo-all-time" title="Permanent link">¶</a>"

    <div id="mojo-all-time" />Uses the [All Time Lists](https://www.boxofficemojo.com/charts/overall/) to collection items.

    <hr style="margin: 0px;">

    **Works With:** Movies, Playlists, and Custom Sort
    
    **Builder Attribute:** `mojo_all_time`

    **Builder Value:** [Dictionary](../../pmm/yaml.md#dictionaries) of Attributes

    ??? blank "`chart` - Determines the chart you want to use"

        Determines the chart you want to use.

        **Allowed Values:** `domestic` or `worldwide`

    ??? blank "`content_rating_filter` - Determines the content rating chart to use"

        Determines the content rating chart to use.

        **Allowed Values:** `g`, `g/pg`, `pg`, `pg-13`, `r` or `nc-17`

    ??? blank "`limit` - The maximum number of result to return"
        
        This determines the maximum number of results to return. If there are less results then the limit then all will 
        be returned. 

        **Default Value:** Returns all results

        **Allowed Values:** Number greter than 0

    ???+ example "Example"
        
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
            mojo_world:
              chart: domestic
              content_rating_filter: g
              limit: 10
        ```

??? blank "`mojo_never` - Uses the Never Hit Lists.<a class="headerlink" href="#mojo-never" title="Permanent link">¶</a>"

    <div id="mojo-never" />Uses the [Never Hit Lists](https://www.boxofficemojo.com/charts/overall/) (Bottom Section) to 
    collection items.

    <hr style="margin: 0px;">

    **Works With:** Movies, Playlists, and Custom Sort
    
    **Builder Attribute:** `mojo_never`

    **Builder Value:** [Dictionary](../../pmm/yaml.md#dictionaries) of Attributes

    ??? blank "`chart` - Determines the chart you want to use"

        Determines the chart you want to use.

        **Allowed Values:** Item in the drop down found [here](https://www.boxofficemojo.com/charts/overall/)

    ??? blank "`never` - Determines the never filter to use"

        Determines the never filter to use.

        **Default Value:** `1`

        **Allowed Values:** `1`, `5`, or `10`

    ??? blank "`limit` - The maximum number of result to return"
        
        This determines the maximum number of results to return. If there are less results then the limit then all will 
        be returned. 

        **Default Value:** Returns all results

        **Allowed Values:** Number greter than 0

    ???+ example "Example"
        
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

??? blank "`mojo_record` - Uses other Record Lists.<a class="headerlink" href="#mojo-record" title="Permanent link">¶</a>"

    <div id="mojo-record" />Uses the [Weekend Records](https://www.boxofficemojo.com/charts/weekend/), 
    [Daily Records](https://www.boxofficemojo.com/charts/daily/), and 
    [Miscellaneous Records](https://www.boxofficemojo.com/charts/misc/) to collection items.

    <hr style="margin: 0px;">

    **Works With:** Movies, Playlists, and Custom Sort
    
    **Builder Attribute:** `mojo_record`

    **Builder Value:** [Dictionary](../../pmm/yaml.md#dictionaries) of Attributes

    ??? blank "`chart` - Determines the record you want to use"

        Determines the chart you want to use.

        **Allowed Values:** `second_weekend_drop`, `post_thanksgiving_weekend_drop`, `top_opening_weekend`, 
        `worst_opening_weekend_theater_avg`, `mlk_opening`, `easter_opening`, `memorial_opening`, `labor_opening`, 
        `president_opening`, `thanksgiving_3_opening`, `thanksgiving_5_opening`, `mlk`, `easter`, `4th`, `memorial`, 
        `labor`, `president`, `thanksgiving_3`, `thanksgiving_5`, `january`, `february`, `march`, `april`, `may`, 
        `june`, `july`, `august`, `september`, `october`, `november`, `december`, `spring`, `summer`, `fall`, 
        `holiday_season`, `winter`, `g`, `g/pg`, `pg`, `pg-13`, `r`, `nc-17`, `top_opening_weekend_theater_avg_all`, 
        `top_opening_weekend_theater_avg_wide`, `opening_day`, `single_day_grosses`, `christmas_day_gross`, 
        `new_years_day_gross`, `friday`, `saturday`, `sunday`, `monday`, `tuesday`, `wednesday`, `thursday`, 
        `friday_non_opening`, `saturday_non_opening`, `sunday_non_opening`, `monday_non_opening`, `tuesday_non_opening`, 
        `wednesday_non_opening`, `thursday_non_opening`, `biggest_theater_drop`, or `opening_week`


    ??? blank "`limit` - The maximum number of result to return"
        
        This determines the maximum number of results to return. If there are less results then the limit then all will 
        be returned. 

        **Default Value:** Returns all results

        **Allowed Values:** Number greter than 0

    ???+ example "Example"
        
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
