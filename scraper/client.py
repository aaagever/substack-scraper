import time
import requests


class SubstackClient:
    """Lightweight client for Substack's API. No third-party wrapper needed."""

    def __init__(self, slug: str, domain: str = None, rate_limit: float = 1.0):
        self.base_url = f"https://{domain}" if domain else f"https://{slug}.substack.com"
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "SubstackScraper/1.0",
            "Accept": "application/json",
        })

    def _get(self, path: str, params: dict = None) -> dict:
        time.sleep(self.rate_limit)
        url = f"{self.base_url}{path}"
        for attempt in range(3):
            resp = self.session.get(url, params=params, timeout=30)
            if resp.status_code == 429:
                wait = 2 ** (attempt + 1)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        resp.raise_for_status()
        return resp.json()

    def get_posts(self, limit: int = None) -> list[dict]:
        """Fetch all posts from the publication, paginated."""
        posts = []
        offset = 0
        page_size = 25

        while True:
            data = self._get("/api/v1/posts", params={"offset": offset, "limit": page_size})
            batch = data if isinstance(data, list) else data.get("posts", data.get("data", []))

            if not batch:
                break

            posts.extend(batch)

            if limit and len(posts) >= limit:
                return posts[:limit]

            if len(batch) < page_size:
                break

            offset += page_size

        return posts

    def get_post(self, slug: str) -> dict:
        """Fetch a single post by its slug."""
        return self._get(f"/api/v1/posts/{slug}")
