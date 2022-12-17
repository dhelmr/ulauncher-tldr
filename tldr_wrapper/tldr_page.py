import dataclasses
import typing

from tldr_wrapper.utils import extract_url, remove_suffix, remove_suffixes


@dataclasses.dataclass
class TldrPage:
    name: str
    raw_content: str


@dataclasses.dataclass
class TldrCommandEntry:
    description: str
    command: str


@dataclasses.dataclass
class StructedTldrPage:
    name: str
    title: str
    description: str
    more_info_url: str
    commands: typing.List[TldrCommandEntry]


class TldrPageParser:
    def __init__(self):
        pass

    def parse_page(self, page: TldrPage) -> StructedTldrPage:
        lines = page.raw_content.splitlines()
        title = ""
        description_lines = []
        more_info_url = ""
        commands = []
        current_entry_description = ""
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                title = stripped[1:].strip()
            elif stripped.startswith(">"):
                if stripped[1:].strip().lower().startswith("more information:"):
                    more_info_url = extract_url(
                        remove_suffixes(
                            stripped[1:].lower(), ".", ">"
                        )
                        .strip()
                    )
                else:
                    description_lines.append(stripped[1:].strip())
            elif stripped.startswith("-"):
                current_entry_description = stripped[1:].strip()
            elif stripped.startswith("`"):
                command = remove_suffix(stripped[1:], "`").strip()
                commands.append(
                    TldrCommandEntry(
                        description=current_entry_description, command=command
                    )
                )
                current_entry_description = ""
        return StructedTldrPage(
            name=page.name,
            title=title,
            description="\n".join(description_lines),
            more_info_url=more_info_url,
            commands=commands,
        )
