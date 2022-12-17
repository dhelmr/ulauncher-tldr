import dataclasses
import os
import os.path
import subprocess
from typing import List, Optional

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
    ):
        self.cache_dir = cache_dir
        self.repo_path = repo_path
        self.lang_suffix = lang_suffix
        self._download_upstream()
        self.pages = self._list_page_names()

    def _download_upstream(self):
        if not os.path.exists(self.cache_dir) or not os.path.isdir(self.cache_dir):
            os.mkdir(self.cache_dir)
        if len(os.listdir(path=self.cache_dir)) == 0:
            git_clone(repo=self.repo_path, local_dir=self.cache_dir)
        # TODO update with git pull/fetch

    def pages_dir(self):
        return os.path.join(self.cache_dir, "pages" + self.lang_suffix)

    def _list_page_names(self) -> List[TldrPageName]:
        pages_root = self.pages_dir()
        root_index = len(pages_root)
        return [
            TldrPageName(full_name=os.path.join(dir_path, f)[root_index+1: -3], name=f[:-3])
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


def git_clone(repo: str, local_dir: str) -> str:
    args = ["git", "clone", repo, local_dir]
    p = subprocess.run(args, encoding="utf-8", capture_output=True)
    if p.stderr == "":
        errs = None
    else:
        errs = p.stderr
    if p.returncode != 0:
        format_cli_line = " ".join(args)
        raise RuntimeError(
            "git clone ended with state %s %s: %s"
            % (p.returncode, format_cli_line, errs)
        )
    output = str(p.stdout)
    return output
