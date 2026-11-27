# Comparing People Posters with the published repositories

`scripts/compare_people_posters.py` renders people with Kometa's People Poster renderer (`modules/people_render.py`) and compares each poster with the published version from the matching `People-Images-<style>` repository. Use it to check that a renderer change still looks like the posters people already have.

## Running it

From the repository root, with the development dependencies installed:

```bash
uv sync --group dev        # once, so fonttools and uharfbuzz are installed
python scripts/compare_people_posters.py
```

With no arguments it checks a default set of 10 people (Tom Hanks, Meryl Streep, Viola Davis and others) in all five styles.

## Options

| Option | What it does | Default |
|:-------|:-------------|:--------|
| Names (positional) | People to compare, spelled exactly as in the repositories. Quote names that contain spaces. | 10 sample people |
| `--styles` | Any of `bw`, `diiivoy`, `diiivoycolor`, `rainier` and `signature`. | All five |
| `--output DIR` | Folder for the comparison images. | `config/people-poster-comparison/` (ignored by git) |
| `--source-repo` | Repository holding the transparent source images. | `People-Images-transparent-1500` |
| `--branch` | Branch to read from. | `master` |

Examples:

```bash
python scripts/compare_people_posters.py "Tom Hanks" "50 Cent" "Robert Downey Jr."
python scripts/compare_people_posters.py "Tom Hanks" --styles rainier signature
python scripts/compare_people_posters.py --output /tmp/people-check
```

## What it produces

1. **One line per person and style** with the mean pixel difference, out of 255, between the published poster (resized to 1000 × 1500) and the local render:

    ```text
    Tom Hanks / rainier: mean difference 1.87 / 255
    ```

    People missing from either repository are reported and skipped.

2. **The average difference for each style** at the end of the run.

3. **Side-by-side images** in the output folder, named `<name>.<style>.jpg`, with the published poster on the left and the local render on the right, plus an `index.html` page showing them all:

    ```bash
    open config/people-poster-comparison/index.html
    ```

## Reading the numbers

| Mean difference | Meaning |
|:----------------|:--------|
| Under about 2 | Visually the same; the remaining difference is text rendering and JPEG noise. Signature is typically about 1, the other styles about 1.7 to 1.9. |
| About 3 to 8 | Something visible changed. Open the side-by-side image to see what. |
| Higher, or a whole style rising at once | Something is really different, such as the subject's position, the artwork or the label layout. |

Two differences in the 3 to 8 range are expected:

* Diiivoy posters published before the Inter Light font change (November 2026) use a thinner font than the current renderer.
* Diiivoycolor and Rainier posters that the old renderer wrongly turned gray, when the subject started low in the frame, now keep their color.

## When to run it

Run it after changing the renderer (`modules/people_render.py`), the artwork in `defaults/images/people/`, or the fonts in `fonts/people/`. If a change is meant to alter the output, also increase `RENDERER_VERSION` in `modules/people_render.py` so users' cached posters are regenerated.

It needs network access to `raw.githubusercontent.com` and takes roughly 30 to 45 seconds for the default set, mostly downloading. It doesn't touch any Kometa config, cache or media server.
