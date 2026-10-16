import re
from markdownify import markdownify as md


def strip_media_tags(html: str) -> str:
    """Remove img, video, iframe, and figure tags (keep text-only)."""
    # Remove figure blocks (may contain images + captions)
    html = re.sub(r"<figure[^>]*>.*?</figure>", "", html, flags=re.DOTALL)
    # Remove standalone tags
    for tag in ("img", "video", "iframe", "source"):
        html = re.sub(rf"<{tag}[^>]*/?>", "", html)
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", html, flags=re.DOTALL)
    return html


def html_to_markdown(html: str) -> str:
    """Convert HTML body to clean markdown."""
    cleaned = strip_media_tags(html)
    markdown = md(cleaned, heading_style="ATX", bullets="-", strip=["div", "span"])
    # Clean up excessive blank lines
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    return markdown.strip()


def build_frontmatter(post: dict, author_name: str, base_url: str) -> str:
    """Build YAML frontmatter string (no YAML library needed)."""
    title = post.get("title", "Untitled").replace('"', '\\"')
    subtitle = (post.get("subtitle") or "").replace('"', '\\"')
    date = (post.get("post_date") or post.get("published_at", ""))[:10]
    slug = post.get("slug", "")
    url = f"{base_url}/p/{slug}"

    lines = [
        "---",
        f'title: "{title}"',
        f'author: "{author_name}"',
        f"date: {date}",
        f"url: {url}",
    ]
    if subtitle:
        lines.append(f'subtitle: "{subtitle}"')
    lines.append("---")
    return "\n".join(lines)


def format_post(post: dict, author_name: str, base_url: str) -> str:
    """Convert a post dict into a complete markdown file string."""
    frontmatter = build_frontmatter(post, author_name, base_url)
    body_html = post.get("body_html", "")

    if not body_html:
        body = "*No content available (may be paywalled)*"
    else:
        body = html_to_markdown(body_html)

    return f"{frontmatter}\n\n{body}\n"
