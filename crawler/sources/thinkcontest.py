from .base import BaseSource

class ThinkContestSource(BaseSource):
    name = "thinkcontest"
    start_urls = [
        "https://www.thinkcontest.com/",
    ]
    link_markers = [
        "/contest/view.do",
    ]
