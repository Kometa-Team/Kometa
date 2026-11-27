---
hide:
  - toc
---
# People Posters Attributes

Kometa generates the styled People Posters (Black & White, Diiivoy, Diiivoy Color, Rainier and Signature) on your machine from a transparent image of each person, which it downloads from GitHub. Generated posters are kept in a cache so each one is only made once.

Configuring `people_posters` is optional; Kometa uses the defaults below when the mapping is missing.

A `people_posters` mapping is in the root of the config file, sampled below.

```yaml title="config.yml People Posters sample"
people_posters:
  original_repo: Kometa-Team/People-Images-1500
  transparent_repo: Kometa-Team/People-Images-transparent-1500
  branch:
  prune_days: 90
  render_limit: 250
```

| Attribute          | Description                                                                                          | Allowed Values (default in **bold**)                     |                 Required                 |
|:-------------------|:-----------------------------------------------------------------------------------------------------|:---------------------------------------------------------|:----------------------------------------:|
| `original_repo`    | GitHub repository holding the original person photographs, which are used as they are.               | `owner/name`, e.g. **`Kometa-Team/People-Images-1500`**  | :fontawesome-solid-circle-xmark:{ .red } |
| `transparent_repo` | GitHub repository holding the transparent person images that styled posters are generated from.     | `owner/name`, e.g. **`Kometa-Team/People-Images-transparent-1500`** | :fontawesome-solid-circle-xmark:{ .red } |
| `branch`           | Branch to read from both repositories.                                                               | Any branch name, or leave **blank** for each repository's default branch | :fontawesome-solid-circle-xmark:{ .red } |
| `prune_days`       | Delete cached posters and source images that no run has used for this many days. `0` keeps them forever. | Integer, e.g. **`90`**                                   | :fontawesome-solid-circle-xmark:{ .red } |
| `render_limit`     | Maximum number of posters to generate in one run. `0` means no limit.                                | Integer, e.g. **`250`**                                  | :fontawesome-solid-circle-xmark:{ .red } |

## How the cache works

Generated posters are saved in `cache/people_posters/<style>/<first letter>/<name>.jpg` next to your config file, and the cache database records which source image and which version of the poster artwork each one was made from.

On each run Kometa asks GitHub once for the list of files in `transparent_repo`. A cached poster is reused unless:

* the person's source image on GitHub has changed, or
* a Kometa update has changed the artwork, fonts or layout for that style.

In either case the poster is generated again and uploaded to your media server on that run. Unchanged posters are not uploaded again.

Downloaded source images are kept in `cache/people_posters/_source` so every style of the same person is made from a single download.

If the `cache` [Setting](settings.md#cache) is `false`, posters are generated in a temporary folder that is deleted at the end of the run, so they are generated again on every run.

## Render limit

The first run after enabling People Posters may need to generate many posters. When `render_limit` is reached, Kometa logs a warning and leaves the remaining people's current posters unchanged; they are generated on later runs. Posters already in the cache are not counted against the limit.

## GitHub token

Kometa makes one GitHub API request per repository per run, which fits within GitHub's limit for anonymous requests. If several programs on your network use the GitHub API, add a [GitHub token](github.md) to avoid being rate limited. When the file list hasn't changed since the last run, GitHub's reply doesn't count against an authenticated token's limit.

The token needs no permissions: a [fine-grained token](https://github.com/settings/personal-access-tokens/new) with **Repository access** set to **Public repositories** and no permissions selected, or a [classic token](https://github.com/settings/tokens/new) with no scopes selected.

If GitHub can't be reached, Kometa uses the file list from the previous run.
