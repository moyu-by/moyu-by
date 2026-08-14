#!/usr/bin/env python3
import json
import os
import urllib.request
from collections import Counter

TOKEN = os.environ.get("GITHUB_TOKEN", "")
USER = os.environ.get("GITHUB_REPOSITORY_OWNER", "moyu-by")

LANG_COLORS = {
    "Java": "#b07219",
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Vue": "#41b883",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Kotlin": "#A97BFF",
    "Shell": "#89e051",
    "C++": "#f34b7d",
    "C": "#555555",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Dockerfile": "#384d54",
    "Makefile": "#427819",
    "SCSS": "#c6538c",
    "PHP": "#4F5D95",
    "C#": "#178600",
    "Ruby": "#701516",
    "Swift": "#F05138",
    "Jupyter Notebook": "#DA5B0B",
    "Objective-C": "#438eff",
    "Elixir": "#6e4a7e",
    "Haskell": "#5e5086",
    "Lua": "#000080",
}


def api(path):
    req = urllib.request.Request("https://api.github.com" + path)
    if TOKEN:
        req.add_header("Authorization", "token " + TOKEN)
    req.add_header("User-Agent", "readme-language-stats")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


repos = []
page = 1
while True:
    batch = api("/users/{0}/repos?per_page=100&page={1}&sort=updated".format(USER, page))
    if not batch or page > 10:
        break
    repos.extend(batch)
    page += 1

lang_bytes = Counter()
for repo in repos:
    if repo.get("fork"):
        continue
    try:
        langs = api("/repos/{0}/{1}/languages".format(USER, repo["name"]))
    except Exception:
        continue
    for name, size in langs.items():
        lang_bytes[name] += size

total = sum(lang_bytes.values())
items = sorted(
    ((name, size) for name, size in lang_bytes.items() if size / total >= 0.005),
    key=lambda kv: -kv[1],
)

WIDTH, HEIGHT = 400, 200
BG, BORDER = "#0D1117", "#30363D"
TITLE, TEXT, SUBTEXT = "#6DB33F", "#8B949E", "#484F58"
BAR_BG = "#21262D"

rows = items[:7]
body = []

body.append(
    '<text x="20" y="30" font-family="Segoe UI, sans-serif" font-size="14" '
    'font-weight="600" fill="{0}">Most Used Languages</text>'.format(TITLE)
)

for i, (name, size) in enumerate(rows):
    y = 52 + i * 20
    pct = size / total * 100
    color = LANG_COLORS.get(name, "#8B949E")
    bar_w = int(200 * size / total)
    body.append(
        '<text x="20" y="{0}" font-family="Segoe UI, sans-serif" font-size="12" '
        'fill="{1}">{2}</text>'.format(y, TEXT, esc(name))
    )
    body.append(
        '<rect x="150" y="{0}" width="200" height="8" rx="4" fill="{1}"/>'.format(y - 9, BAR_BG)
    )
    if bar_w > 0:
        body.append(
            '<rect x="150" y="{0}" width="{1}" height="8" rx="4" fill="{2}"/>'.format(y - 9, bar_w, color)
        )
    body.append(
        '<text x="362" y="{0}" text-anchor="end" font-family="Segoe UI, sans-serif" '
        'font-size="12" fill="{1}">{2:.1f}%</text>'.format(y, TEXT, pct)
    )

footer_y = 52 + len(rows) * 20 + 10
body.append(
    '<text x="20" y="{0}" font-family="Segoe UI, sans-serif" font-size="10" '
    'fill="{1}">Auto-generated via GitHub Actions</text>'.format(footer_y, SUBTEXT)
)

svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="{0}" height="{1}" '
    'viewBox="0 0 {0} {1}">'.format(WIDTH, HEIGHT)
    + '<rect width="{0}" height="{1}" rx="10" fill="{2}" stroke="{3}" stroke-width="1"/>'.format(
        WIDTH, HEIGHT, BG, BORDER
    )
    + "".join(body)
    + "</svg>"
)

os.makedirs("dist", exist_ok=True)
with open("dist/languages.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("generated dist/languages.svg with {0} languages".format(len(rows)))
