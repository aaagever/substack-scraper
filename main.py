#!/usr/bin/env python3
"""Substack Article Scraper — scrapes newsletter posts to markdown files."""

import argparse
import json
import os
import sys

from scraper.client import SubstackClient
from scraper.formatter import format_post
from scraper.storage import post_filename, save_post, generate_index


def load_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return json.load(f)


def scrape_author(author: dict, settings: dict, force: bool = False, limit: int = None):
    name = author["name"]
    slug = author["slug"]
    domain = author.get("domain")
    output_dir = os.path.join(settings["output_root"], author["output_dir"])
    base_url = f"https://{domain}" if domain else f"https://{slug}.substack.com"

    print(f"\n{'='*60}")
    print(f"Scraping: {name} ({base_url})")
    print(f"Output:   {output_dir}")
    print(f"{'='*60}")

    client = SubstackClient(slug, domain=domain)

    print("Fetching post list...")
    posts = client.get_posts(limit=limit)
    print(f"Found {len(posts)} posts")

    written = 0
    skipped = 0

    for i, post in enumerate(posts, 1):
        title = post.get("title", "Untitled")
        filename = post_filename(post)

        # Check if we need full content
        if not post.get("body_html"):
            post_slug = post.get("slug")
            if post_slug:
                try:
                    full_post = client.get_post(post_slug)
                    post.update(full_post)
                except Exception as e:
                    print(f"  [{i}/{len(posts)}] WARN: Could not fetch full post '{title}': {e}")

        content = format_post(post, name, base_url)
        was_written = save_post(content, filename, output_dir, force=force)

        if was_written:
            written += 1
            print(f"  [{i}/{len(posts)}] Saved: {filename}")
        else:
            skipped += 1
            print(f"  [{i}/{len(posts)}] Skipped (exists): {filename}")

    generate_index(name, posts, output_dir, base_url)
    print(f"\nDone: {written} saved, {skipped} skipped, _index.md updated")


def main():
    parser = argparse.ArgumentParser(description="Scrape Substack newsletters to markdown")
    parser.add_argument("--author", help="Author output_dir from config (e.g. example-author)")
    parser.add_argument("--all", action="store_true", help="Scrape all authors in config")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--limit", type=int, help="Max number of posts to fetch per author")
    parser.add_argument("--config", default="config.json", help="Path to config file")

    args = parser.parse_args()

    if not args.author and not args.all:
        parser.error("Specify --author <name> or --all")

    config = load_config(args.config)
    authors = config["authors"]
    settings = config["settings"]

    if args.author:
        match = [a for a in authors if a["output_dir"] == args.author]
        if not match:
            available = ", ".join(a["output_dir"] for a in authors)
            print(f"Error: Author '{args.author}' not found. Available: {available}")
            sys.exit(1)
        authors = match

    for author in authors:
        scrape_author(author, settings, force=args.force, limit=args.limit)


if __name__ == "__main__":
    main()
