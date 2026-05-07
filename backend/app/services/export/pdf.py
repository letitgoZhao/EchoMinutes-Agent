from dataclasses import dataclass
from pathlib import Path
from textwrap import wrap

from app.services.export.markdown_blocks import MarkdownBlock, parse_markdown_blocks

PAGE_WIDTH = 612
PAGE_HEIGHT = 792
MARGIN_X = 48
MARGIN_TOP = 54
MARGIN_BOTTOM = 54


@dataclass(frozen=True)
class PdfLine:
    text: str
    size: int = 11
    leading: int = 15
    indent: int = 0
    gap_before: int = 0


def write_pdf_export(title: str, markdown: str, target_path: Path) -> None:
    lines = _markdown_to_pdf_lines(title, markdown)
    pages = _paginate(lines)
    objects: list[bytes] = []

    font_object_id = 3 + len(pages) * 2
    cid_font_object_id = font_object_id + 1
    descriptor_object_id = font_object_id + 2
    info_object_id = font_object_id + 3
    page_ids = [3 + index * 2 for index in range(len(pages))]
    content_ids = [4 + index * 2 for index in range(len(pages))]

    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii"))

    for content_id, page_lines in zip(content_ids, pages, strict=True):
        page = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 {font_object_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )
        objects.append(page.encode("ascii"))
        stream = _build_text_stream(page_lines)
        objects.append(
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"endstream"
        )

    objects.append(
        (
            f"<< /Type /Font /Subtype /Type0 /BaseFont /STSong-Light "
            f"/Encoding /UniGB-UCS2-H /DescendantFonts [{cid_font_object_id} 0 R] >>"
        ).encode("ascii")
    )
    objects.append(
        (
            f"<< /Type /Font /Subtype /CIDFontType0 /BaseFont /STSong-Light "
            f"/CIDSystemInfo << /Registry (Adobe) /Ordering (GB1) /Supplement 5 >> "
            f"/FontDescriptor {descriptor_object_id} 0 R >>"
        ).encode("ascii")
    )
    objects.append(
        b"<< /Type /FontDescriptor /FontName /STSong-Light /Flags 6 "
        b"/FontBBox [0 -200 1000 900] /ItalicAngle 0 /Ascent 880 "
        b"/Descent -120 /CapHeight 700 /StemV 80 >>"
    )
    objects.append(
        (
            f"<< /Title ({_escape_pdf_literal(title)}) "
            f"/Producer (EchoMinutes Agent) >>"
        ).encode("ascii")
    )
    pdf_bytes = _assemble_pdf(objects, info_object_id=info_object_id)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(pdf_bytes)


def _markdown_to_pdf_lines(title: str, markdown: str) -> list[PdfLine]:
    lines = [PdfLine(title, size=18, leading=24), PdfLine("", leading=8)]
    for block in parse_markdown_blocks(markdown):
        lines.extend(_block_to_pdf_lines(block))
    return lines


def _block_to_pdf_lines(block: MarkdownBlock) -> list[PdfLine]:
    if block.kind == "blank":
        return [PdfLine("", leading=8)]
    if block.kind == "heading":
        size = {1: 17, 2: 14, 3: 12}.get(block.level, 12)
        return [
            PdfLine(text, size=size, leading=size + 7, gap_before=8)
            for text in _wrap_text(block.text, width=max(28, 72 - block.level * 4))
        ]
    if block.kind == "bullet":
        wrapped = _wrap_text(block.text, width=72)
        return [
            PdfLine(f"- {wrapped[0]}", indent=10),
            *[PdfLine(line, indent=22) for line in wrapped[1:]],
        ]
    if block.kind == "numbered":
        wrapped = _wrap_text(block.text, width=70)
        return [
            PdfLine(f"{block.number} {wrapped[0]}", indent=10),
            *[PdfLine(line, indent=26) for line in wrapped[1:]],
        ]
    return [PdfLine(line) for line in _wrap_text(block.text, width=78)]


def _wrap_text(text: str, width: int) -> list[str]:
    return wrap(
        text,
        width=width,
        break_long_words=True,
        replace_whitespace=False,
    ) or [""]


def _paginate(lines: list[PdfLine]) -> list[list[PdfLine]]:
    pages: list[list[PdfLine]] = [[]]
    remaining = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM
    for line in lines:
        needed = line.leading + line.gap_before
        if pages[-1] and needed > remaining:
            pages.append([])
            remaining = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM
        pages[-1].append(line)
        remaining -= needed
    return pages


def _build_text_stream(lines: list[PdfLine]) -> bytes:
    commands: list[str] = []
    y = PAGE_HEIGHT - MARGIN_TOP
    for line in lines:
        y -= line.gap_before
        commands.append("BT")
        commands.append(f"/F1 {line.size} Tf")
        commands.append(f"1 0 0 1 {MARGIN_X + line.indent} {y} Tm")
        commands.append(f"<{_encode_pdf_text(line.text)}> Tj")
        commands.append("ET")
        y -= line.leading
    return ("\n".join(commands) + "\n").encode("ascii")


def _encode_pdf_text(value: str) -> str:
    return value.encode("utf-16-be", errors="replace").hex().upper()


def _escape_pdf_literal(value: str) -> str:
    return (
        value.encode("ascii", errors="ignore")
        .decode("ascii")
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def _assemble_pdf(objects: list[bytes], *, info_object_id: int) -> bytes:
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_id, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{object_id} 0 obj\n".encode("ascii"))
        output.extend(body)
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            "trailer\n"
            f"<< /Size {len(objects) + 1} /Root 1 0 R /Info {info_object_id} 0 R >>\n"
            "startxref\n"
            f"{xref_offset}\n"
            "%%EOF\n"
        ).encode("ascii")
    )
    return bytes(output)
