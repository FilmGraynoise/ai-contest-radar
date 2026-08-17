from .base import BaseSource

class WevitySource(BaseSource):
    name = "wevity"
    start_urls = [
        "https://www.wevity.com/?c=find&s=1",
        "https://www.wevity.com/index.php?c=find&s=1",
    ]
    link_markers = [
        "gbn=view",
    ]
