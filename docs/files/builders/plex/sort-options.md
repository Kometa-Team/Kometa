# Sort Options

<!--shared-content-start-->
## Plex sort options

Append `.asc` for ascending or `.desc` for descending order, such as
`audience_rating.desc`. `random` stands alone, without a direction suffix.
Choose a field supported by the selected item level. To sort by several fields,
supply a YAML list; earlier fields take priority.

| Field | Orders by | Supports |
|:------|:----------|:---------|
| `title` | Title | Movies, Shows, Episodes, Artists, Albums, Tracks |
| `season` | Season | Seasons |
| `show` | Show | Seasons, Episodes |
| `album_artist` | Album Artist | Albums, Tracks |
| `artist` | Artist | Tracks |
| `album` | Album | Tracks |
| `year` | Year | Movies, Shows, Episodes, Albums |
| `release` | Release Date (Originally Available) | Movies, Shows, Episodes, Albums |
| `episode_release` | Episode Release Date (Originally Available) | Shows, Seasons, Episodes |
| `critic_rating` | Critic Rating | Movies, Shows, Episodes, Albums |
| `audience_rating` | Audience Rating | Movies, Shows, Episodes |
| `user_rating` | User Rating | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `content_rating` | Content Rating | Movies, Shows |
| `duration` | Duration | Movies, Episodes, Tracks |
| `progress` | Progress | Episodes |
| `played` | Date Last Played | Artists, Albums, Tracks |
| `plays` | Number of Plays | Movies, Episodes, Artists, Albums, Tracks |
| `unplayed` | Unplayed | Shows |
| `episode_added` | Last Episode Date Added | Shows |
| `added` | Date Added | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `viewed` | Date Last Viewed | Movies, Shows, Episodes |
| `rated` | Date Last Rated | Tracks |
| `popularity` | Popularity | Tracks |
| `resolution` | Resolution | Movies, Episodes |
| `bitrate` | Bitrate | Movies, Episodes, Tracks |
| `random` | Random | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
