import os
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.event import PreferencesEvent
from ulauncher.api.shared.event import ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from  ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
import os.path
import html
from enum import Enum

from tldr_wrapper.client import TldrClient
from tldr_wrapper.tldr_page import TldrPageParser


class ExtensionState(Enum):
    STARTING = "Extension is starting..."
    DBANG_LOADING_FAILED = (
        "Could not load successfully. Please restart ulauncher. and check logs"
    )
    READY = "ok"

    def __str__(self):
        return self.value


class TldrExt(Extension):
    def __init__(self):
        super(TldrExt, self).__init__()
        self.tldr_client = TldrClient()
        self.tldr_parser = TldrPageParser()
        self.subscribe(KeywordQueryEvent, KeywordQueryListener())


class KeywordQueryListener(EventListener):
    def on_event(self, event, ext: TldrExt):
        argument = event.get_argument()
        if argument is None or argument == "":
            return self.list_commands(ext)

        search_results = self.run_search(ext, argument)
        return search_results

    def run_search(self, ext:TldrExt, argument: str):
        if "/" in argument:
            action = self.display_page(ext, argument.strip())
            if action is not None:
                return action
        results = ext.tldr_client.search_page_names(argument)
        if len(results) == 0:
            splitted_arguments = argument.split(" ")
            if len(splitted_arguments) > 1:
                new_search_term = " ".join(splitted_arguments[:-1])
                return self.run_search(ext, new_search_term)
            else:
                return self.nothing_found(ext)
        elif len(results) == 1 or results[0].name.lower() == argument.strip().lower():
            return self.display_page(ext, results[0].full_name)
        return RenderResultListAction([
            ExtensionResultItem(name="%s" % r.name,
                                description="open tldr for %s" % r.full_name,
                                icon="icons/page.svg",
                                on_enter=SetUserQueryAction(self._make_page_query(ext, r.full_name)))
            for r in results[:int(ext.preferences["max_search_result_size"])]
        ])

    def display_page(self, ext: TldrExt, page_name: str):
        page = ext.tldr_client.get_page(page_name)
        if page is None:
            return None
        try:
            parsed = ext.tldr_parser.parse_page(page)
        except Exception as e:
            return # todo
        return RenderResultListAction([
            ExtensionResultItem(name=parsed.title,
                                description=pad_string(parsed.description, width=90),
                                icon="icons/information.svg", highlightable=False)
        ]+[
            ExtensionResultItem(name=command.command.removesuffix(".").removesuffix(":"), description=command.description,
                                icon="icons/command.svg", on_enter=CopyToClipboardAction(command.command))
            for command in parsed.commands
        ]+[
            ExtensionResultItem(name="More information: %s" % parsed.more_info_url, description="[open in webbrowser]", icon="icons/external_url.svg",
                                on_enter=OpenUrlAction(parsed.more_info_url))
        ])

    def list_commands(self, ext: TldrExt):
        return RenderResultListAction([])

    def nothing_found(self, ext: TldrExt):
        return RenderResultListAction([
            ExtensionResultItem("No tldr page could be found :(")
        ])

    def _make_page_query(self, ext: TldrExt, page_name: str):
        return "%s %s " % (ext.preferences["keyword"], page_name)

def pad_string(text: str, width: int):
    padded_lines = [""]
    for line in text.splitlines():
        for word in line.split(" "):
            if len(word) + len(padded_lines[-1]) < width:
                padded_lines[-1] += word + " "
            else:
                padded_lines.append(word+" ")
    return "\n".join(padded_lines)

if __name__ == "__main__":
    TldrExt().run()
