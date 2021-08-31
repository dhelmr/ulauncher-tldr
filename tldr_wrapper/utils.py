import re


def extract_url(text: str):
    return re.search("(?P<url>https?://[^\s]+)", text).group("url")
