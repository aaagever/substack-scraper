import os
import re


def slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:80].strip("-")


def post_filename(post: dict) -> str:
    """Generate filename: YYYY-MM-DD-slugified-title.md"""
    date = (post.get("post_date") or post.get("published_at", ""))[:10]
    title_slug = slugify(post.get("title", "untitled"))
    return f"{date}-{title_slug}.md"


def save_post(content: str, filename: str, output_dir: str, force: bool = False) -> bool:
    """Write markdown file to disk. Returns True if written, False if skipped."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    if os.path.exists(filepath) and not force:
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def generate_index(author_name: str, posts: list[dict], output_dir: str, base_url: str):
    """Generate _index.md with author metadata and article listing."""
    os.makedirs(output_dir, exist_ok=True)

    lines = [
        f"# {author_name}",
        "",
        f"Source: {base_url}",
        f"Total articles: {len(posts)}",
        "",
        "## Articles",
        "",
    ]

    # Sort by date descending
    sorted_posts = sorted(posts, key=lambda p: p.get("post_date") or p.get("published_at", ""), reverse=True)

    for post in sorted_posts:
        date = (post.get("post_date") or post.get("published_at", ""))[:10]
        title = post.get("title", "Untitled")
        filename = post_filename(post)
        lines.append(f"- **{date}** — [{title}]({filename})")

    lines.append("")

    filepath = os.path.join(output_dir, "_index.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
