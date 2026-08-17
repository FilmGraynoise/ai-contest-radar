from .base import BaseSource


class ContestKoreaSource(BaseSource):
    name = "contestkorea"

    start_urls = [
        "https://www.contestkorea.com/sub/list.php",
    ]

    link_markers = [
        "/sub/view.php",
    ]
