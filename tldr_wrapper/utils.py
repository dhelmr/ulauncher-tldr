import re


def extract_url(text: str):
    return re.search("(?P<url>https?://[^\s]+)", text).group("url")


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


def remove_suffixes(input_string, *suffixes):
    curr_input = input_string
    for suffix in suffixes:
        curr_input = remove_suffix(curr_input, suffix)
    return curr_input


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text
