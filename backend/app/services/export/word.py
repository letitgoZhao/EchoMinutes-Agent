from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


def write_word_export(markdown: str, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    document_xml = _build_document_xml(markdown)
    with ZipFile(target_path, "w", ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", _content_types_xml())
        docx.writestr("_rels/.rels", _root_relationships_xml())
        docx.writestr("word/document.xml", document_xml)
        docx.writestr("word/_rels/document.xml.rels", _document_relationships_xml())


def _build_document_xml(markdown: str) -> str:
    paragraphs = "\n".join(_paragraph_xml(line) for line in markdown.splitlines())
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {paragraphs}
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>
    </w:sectPr>
  </w:body>
</w:document>
"""


def _paragraph_xml(line: str) -> str:
    style = ""
    text = line.strip()
    if text.startswith("#"):
        level = min(len(text) - len(text.lstrip("#")), 3)
        text = text.lstrip("#").strip()
        style = f"<w:pStyle w:val=\"Heading{level}\"/>"
    elif text.startswith("- "):
        text = f"• {text[2:]}"

    return (
        "<w:p>"
        f"<w:pPr>{style}</w:pPr>"
        f"<w:r><w:t xml:space=\"preserve\">{escape(text)}</w:t></w:r>"
        "</w:p>"
    )


def _content_types_xml() -> str:
    package_content_type = "application/vnd.openxmlformats-package.relationships+xml"
    document_content_type = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="{package_content_type}"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="{document_content_type}"/>
</Types>
"""


def _root_relationships_xml() -> str:
    relationship_type = (
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="{relationship_type}" Target="word/document.xml"/>
</Relationships>
"""


def _document_relationships_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""
