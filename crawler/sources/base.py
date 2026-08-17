import os
import time
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

@dataclass
class RawContest:
    source: str
    source_url: str
    title: str
    body: str

class BaseSource:
    name = "base"
    start_urls: list[str] = []
    link_markers: list[str] = []

    def __init__(self):
        self.max_links = int(os.getenv("MAX_LINKS_PER_SOURCE", "40"))
        self.delay = float(os.getenv("REQUEST_DELAY_SECONDS", "1.5"))
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AIContestRadar/0.1 (+personal research project; respectful low-frequency crawler)",
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.7",
        })

    def get(self, url: str) -> requests.Response:
        response = self.session.get(url, timeout=20)
        if response.status_code in (403, 429):
            raise RuntimeError(
                f"{self.name}: server returned {response.status_code}. "
                "Do not bypass access controls; disable this source and review its policy."
            )
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding
        return response

    def discover(self) -> list[str]:
        found: list[str] = []
        seen: set[str] = set()

        for start_url in self.start_urls:
            try:
                html = self.get(start_url).text
            except Exception as exc:
                print(f"[WARN] {self.name} listing failed: {exc}")
                continue

            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                absolute = urljoin(start_url, href)
                if not self._same_host(start_url, absolute):
                    continue
                if not any(marker in absolute for marker in self.link_markers):
                    continue
                if absolute in seen:
                    continue

                seen.add(absolute)
                found.append(absolute)
                if len(found) >= self.max_links:
                    return found

        return found

    def fetch_detail(self, url: str) -> RawContest:
        time.sleep(self.delay)
        html = self.get(url).text
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()

        title = ""
        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            title = og.get("content", "").strip()

        if not title:
            for selector in ["h1", "h2", "h3", "title"]:
                node = soup.select_one(selector)
                if node and node.get_text(" ", strip=True):
                    title = node.get_text(" ", strip=True)
                    break

        body = soup.get_text("\n", strip=True)
        # Avoid sending huge navigation/footer text to the model.
        body = body[:30000]

        return RawContest(
            source=self.name,
            source_url=url,
            title=title[:500],
            body=body,
        )

    @staticmethod
    def _same_host(a: str, b: str) -> bool:
        return urlparse(a).netloc == urlparse(b).netloc
