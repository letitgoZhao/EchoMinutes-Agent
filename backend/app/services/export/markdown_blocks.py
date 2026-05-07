from dataclasses import dataclass
from typing import Literal

BlockKind = Literal["heading", "bullet", "numbered", "paragraph", "blank"]


@dataclass(frozen=True)
class MarkdownBlock:
    kind: BlockKind
    text: str = ""
    level: int = 0
    number: str = ""


def parse_markdown_blocks(markdown: str) -> list[MarkdownBlock]:
    blocks: list[MarkdownBlock] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            blocks.append(MarkdownBlock(kind="blank"))
            continue

        heading_level = len(line) - len(line.lstrip("#"))
        if 1 <= heading_level <= 6 and line[heading_level:].startswith(" "):
            blocks.append(
                MarkdownBlock(
                    kind="heading",
                    level=min(heading_level, 3),
                    text=line[heading_level:].strip(),
                )
            )
            continue

        if line.startswith(("- ", "* ")):
            blocks.append(MarkdownBlock(kind="bullet", text=line[2:].strip()))
            continue

        number, numbered_text = _split_numbered_item(line)
        if number and numbered_text:
            blocks.append(
                MarkdownBlock(kind="numbered", number=number, text=numbered_text)
            )
            continue

        blocks.append(MarkdownBlock(kind="paragraph", text=line))
    return blocks or [MarkdownBlock(kind="blank")]


def _split_numbered_item(line: str) -> tuple[str, str]:
    marker, _, remainder = line.partition(". ")
    if marker.isdigit() and remainder.strip():
        return f"{marker}.", remainder.strip()
    return "", ""
