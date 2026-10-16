# Substack Scraper

Save the public posts of Substack newsletters you follow as clean Markdown files, one folder per author, for offline reading and personal research.

- Text only: images, video and embeds are stripped.
- Each post gets YAML frontmatter (title, author, date, URL, subtitle).
- Each author folder gets an `_index.md` listing every post, newest first.
- Re-runs skip posts already saved, so you can run it again to pick up new posts.

## Setup

Requires Python 3.9+.

```bash
pip install -r requirements.txt
cp config.example.json config.json
```

Edit `config.json` and list the newsletters you want:

| Field | Meaning |
|---|---|
| `name` | Author name, written into each post's frontmatter |
| `slug` | The Substack subdomain, e.g. `exampleauthor` for `exampleauthor.substack.com` |
| `domain` | Optional. Use when the newsletter lives on a custom domain |
| `output_dir` | Folder name under `output_root`, also the name you pass to `--author` |

`config.json` and `output/` are git-ignored, so your author list and scraped posts stay local.

## Usage

```bash
python main.py --author example-author            # one author
python main.py --all                              # every author in config.json
python main.py --author example-author --limit 10 # only the 10 most recent posts
python main.py --all --force                      # overwrite files already saved
```

Output lands in `output/<output_dir>/YYYY-MM-DD-post-title.md`.

## How it works

It reads the JSON endpoints every Substack publication serves (`/api/v1/posts`), waits one second between requests and backs off when rate limited. It does not log in. Paywalled posts come back with only their free preview, or a placeholder when there is none.

These endpoints are not an official, documented API, so they may change without notice.

## Use it responsibly

Posts belong to their authors. This tool is meant for personal reading and research: don't republish or redistribute what you download, and respect each publication's terms.

## License

MIT, see [LICENSE](LICENSE). The license covers this code only, not any content you download with it.
