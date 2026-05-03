from pathlib import Path
from textwrap import wrap


def write_pdf_export(title: str, markdown: str, target_path: Path) -> None:
    lines = _markdown_to_pdf_lines(title, markdown)
    pages = _chunk_lines(lines, max_lines=42)
    objects: list[bytes] = []

    font_object_id = 3 + len(pages) * 2
    cid_font_object_id = font_object_id + 1
    descriptor_object_id = font_object_id + 2
    page_ids = [3 + index * 2 for index in range(len(pages))]
    content_ids = [4 + index * 2 for index in range(len(pages))]

    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii"))

    for _page_id, content_id, page_lines in zip(page_ids, content_ids, pages, strict=True):
        page = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
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
    pdf_bytes = _assemble_pdf(objects)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(pdf_bytes)


def _markdown_to_pdf_lines(title: str, markdown: str) -> list[str]:
    content_lines = [title, ""]
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            content_lines.append("")
            continue
        if line.startswith("#"):
            line = line.lstrip("#").strip().upper()
        elif line.startswith("- "):
            line = f"• {line[2:]}"
        content_lines.extend(wrap(line, width=82) or [""])
    return content_lines


def _chunk_lines(lines: list[str], max_lines: int) -> list[list[str]]:
    return [lines[index : index + max_lines] for index in range(0, len(lines), max_lines)] or [[]]


def _build_text_stream(lines: list[str]) -> bytes:
    commands = ["BT", "/F1 11 Tf", "48 744 Td", "14 TL"]
    for index, line in enumerate(lines):
        if index:
            commands.append("T*")
        commands.append(f"<{_encode_pdf_text(line)}> Tj")
    commands.append("ET")
    return ("\n".join(commands) + "\n").encode("ascii")


def _encode_pdf_text(value: str) -> str:
    return value.encode("utf-16-be", errors="replace").hex().upper()


def _assemble_pdf(objects: list[bytes]) -> bytes:
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
            f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            "startxref\n"
            f"{xref_offset}\n"
            "%%EOF\n"
        ).encode("ascii")
    )
    return bytes(output)
