"""Compare Kometa's locally rendered People Posters with the published People-Images-<style> repositories."""

import argparse
import html
import sys
import urllib.parse
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.people_render import SIZE, STYLES, PeopleRenderer  # noqa: E402

RAW = "https://raw.githubusercontent.com/Kometa-Team"
DEFAULT_NAMES = ["Tom Hanks", "Meryl Streep", "Samuel L. Jackson", "Chae Soo-bin", "Pedro Pascal", "Viola Davis", "Robert Downey Jr.", "Lupita Nyong'o", "Gael García Bernal", "Mahershala Ali"]


def fetch(repo, branch, name, suffix):
    url = f"{RAW}/{repo}/{branch}/{name[0].upper()}/Images/{urllib.parse.quote(name)}{suffix}"
    response = requests.get(url, timeout=60)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    image = Image.open(BytesIO(response.content))
    image.load()
    return image


def mean_difference(first, second):
    return sum(ImageStat.Stat(ImageChops.difference(first.convert("RGB"), second.convert("RGB"))).mean) / 3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="*", default=DEFAULT_NAMES, help="People to compare, as named in the repositories")
    parser.add_argument("--source-repo", default="People-Images-transparent-1500")
    parser.add_argument("--branch", default="master")
    parser.add_argument("--styles", nargs="+", default=list(STYLES), choices=STYLES)
    parser.add_argument("--output", type=Path, default=ROOT / "config" / "people-poster-comparison")
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    renderer = PeopleRenderer()
    rows, totals = [], {style: [] for style in args.styles}
    for name in args.names:
        source = fetch(args.source_repo, args.branch, name, ".png")
        if source is None:
            print(f"{name}: not found in {args.source_repo}")
            continue
        for style in args.styles:
            reference = fetch(f"People-Images-{style}", args.branch, name, ".jpg")
            if reference is None:
                print(f"{name} / {style}: no published reference")
                continue
            reference = reference.convert("RGB").resize(SIZE, Image.Resampling.LANCZOS)
            rendered = renderer.render(source, name, style).convert("RGB")
            difference = mean_difference(reference, rendered)
            totals[style].append(difference)
            sheet = Image.new("RGB", (SIZE[0] * 2, SIZE[1]))
            sheet.paste(reference, (0, 0))
            sheet.paste(rendered, (SIZE[0], 0))
            filename = f"{name}.{style}.jpg"
            sheet.save(args.output / filename, quality=90)
            rows.append((name, style, difference, filename))
            print(f"{name} / {style}: mean difference {difference:.2f} / 255")

    print("\nStyle averages (published reference vs. local render):")
    for style, values in totals.items():
        if values:
            print(f"  {style:<13} {sum(values) / len(values):6.2f} / 255 over {len(values)} people")

    cells = "".join(f"<figure><img src='{html.escape(urllib.parse.quote(f))}' loading='lazy'><figcaption>{html.escape(n)} / {s}: {d:.2f}</figcaption></figure>" for n, s, d, f in rows)
    page = f"<!doctype html><meta charset='utf-8'><title>People Poster comparison</title><style>body{{font-family:sans-serif;background:#222;color:#eee}}figure{{display:inline-block;margin:8px}}img{{width:400px}}</style><p>Left: published (downscaled). Right: local render.</p>{cells}"
    (args.output / "index.html").write_text(page, encoding="utf-8")
    print(f"\nSide-by-side sheets: {args.output / 'index.html'}")


if __name__ == "__main__":
    main()
