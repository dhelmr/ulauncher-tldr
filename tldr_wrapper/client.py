import dataclasses
import os
import os.path
import logging
from typing import List, Optional

from tldr_wrapper.git import git_clone, git_pull
from tldr_wrapper.tldr_page import TldrPage, TldrPageParser

DEFAULT_CACHE_DIR = os.path.join(os.environ["HOME"], ".cache", "tldr-python")
DEFAULT_TLDR_REPO_PATH = "https://github.com/tldr-pages/tldr"


@dataclasses.dataclass
class TldrPageName:
    full_name: str
    name: str


class TldrClient:
    def __init__(
            self,
            cache_dir=DEFAULT_CACHE_DIR,
            repo_path=DEFAULT_TLDR_REPO_PATH,
            lang_suffix="",
            update_startup=True
    ):
        self.cache_dir = cache_dir
        self.repo_path = repo_path
        self.lang_suffix = lang_suffix
        self._download_upstream(update_startup)
        self.pages = self._list_page_names()

    def _download_upstream(self, update):
        if not os.path.exists(self.cache_dir) or not os.path.isdir(self.cache_dir):
            os.mkdir(self.cache_dir)
        if len(os.listdir(path=self.cache_dir)) == 0:
            git_clone(repo=self.repo_path, local_dir=self.cache_dir)
        elif update:
            try:
                git_pull(local_dir=self.cache_dir)
            except RuntimeError as e:
                logging.error("Could not update tldr-pages: %s", e)

    def pages_dir(self):
        return os.path.join(self.cache_dir, "pages" + self.lang_suffix)

    def _list_page_names(self) -> List[TldrPageName]:
        pages_root = self.pages_dir()
        root_index = len(pages_root)
        return [
            TldrPageName(full_name=os.path.join(dir_path, f)[root_index + 1: -3], name=f[:-3])
            for dir_path, _, files in os.walk(pages_root)
            for f in files
            if f.endswith(".md")
        ]

    def search_page_names(self, search_text: str) -> List[TldrPageName]:
        search_pattern = search_text.lower()
        return sorted(
            [page for page in self.pages if page.name.lower().startswith(search_pattern)],
            key=lambda item: len(item.name)
        )

    def get_page(self, full_name: str) -> Optional[TldrPage]:
        page_path = os.path.join(self.pages_dir(), full_name + ".md")
        if not os.path.exists(page_path):
            return None
        with open(page_path) as f:
            content = f.read()
        return TldrPage(name=full_name, raw_content=content)
