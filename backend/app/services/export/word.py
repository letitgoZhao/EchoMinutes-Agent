from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from app.services.export.markdown_blocks import MarkdownBlock, parse_markdown_blocks


def write_word_export(title: str, markdown: str, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(target_path, "w", ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", _content_types_xml())
        docx.writestr("_rels/.rels", _root_relationships_xml())
        docx.writestr("docProps/core.xml", _core_properties_xml(title))
        docx.writestr("docProps/app.xml", _app_properties_xml())
        docx.writestr("word/document.xml", _build_document_xml(title, markdown))
        docx.writestr("word/styles.xml", _styles_xml())
        docx.writestr("word/numbering.xml", _numbering_xml())
        docx.writestr("word/_rels/document.xml.rels", _document_relationships_xml())


def _build_document_xml(title: str, markdown: str) -> str:
    paragraphs = [_paragraph_xml(MarkdownBlock(kind="heading", level=1, text=title))]
    paragraphs.extend(_paragraph_xml(block) for block in parse_markdown_blocks(markdown))
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {"".join(paragraphs)}
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080"/>
    </w:sectPr>
  </w:body>
</w:document>
"""


def _paragraph_xml(block: MarkdownBlock) -> str:
    if block.kind == "blank":
        return '<w:p><w:pPr><w:spacing w:after="120"/></w:pPr></w:p>'

    style = ""
    numbering = ""
    text = block.text
    if block.kind == "heading":
        style = f'<w:pStyle w:val="Heading{min(max(block.level, 1), 3)}"/>'
    elif block.kind == "bullet":
        style = '<w:pStyle w:val="ListParagraph"/>'
        numbering = '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
    elif block.kind == "numbered":
        style = '<w:pStyle w:val="ListParagraph"/>'
        numbering = '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="2"/></w:numPr>'

    return (
        "<w:p>"
        f"<w:pPr>{style}{numbering}<w:spacing w:after=\"120\"/></w:pPr>"
        f'<w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'
        "</w:p>"
    )


def _content_types_xml() -> str:
    package_content_type = "application/vnd.openxmlformats-package.relationships+xml"
    document_content_type = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
    )
    core_type = "application/vnd.openxmlformats-package.core-properties+xml"
    app_type = "application/vnd.openxmlformats-officedocument.extended-properties+xml"
    styles_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"
    numbering_type = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="{package_content_type}"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="{document_content_type}"/>
  <Override PartName="/word/styles.xml" ContentType="{styles_type}"/>
  <Override PartName="/word/numbering.xml" ContentType="{numbering_type}"/>
  <Override PartName="/docProps/core.xml" ContentType="{core_type}"/>
  <Override PartName="/docProps/app.xml" ContentType="{app_type}"/>
</Types>
"""


def _root_relationships_xml() -> str:
    document_type = (
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
    )
    core_type = "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties"
    app_type = (
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties"
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="{document_type}" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="{core_type}" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="{app_type}" Target="docProps/app.xml"/>
</Relationships>
"""


def _document_relationships_xml() -> str:
    styles_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles"
    numbering_type = (
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering"
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="{styles_type}" Target="styles.xml"/>
  <Relationship Id="rId2" Type="{numbering_type}" Target="numbering.xml"/>
</Relationships>
"""


def _core_properties_xml(title: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties
  xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:dcmitype="http://purl.org/dc/dcmitype/"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{escape(title)}</dc:title>
  <dc:creator>EchoMinutes Agent</dc:creator>
</cp:coreProperties>
"""


def _app_properties_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
  xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>EchoMinutes Agent</Application>
</Properties>
"""


def _styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:rPr><w:rFonts w:ascii="Arial" w:eastAsia="Microsoft YaHei"/><w:sz w:val="22"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:qFormat/>
    <w:pPr><w:spacing w:before="240" w:after="160"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:qFormat/>
    <w:pPr><w:spacing w:before="220" w:after="120"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="26"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:qFormat/>
    <w:pPr><w:spacing w:before="180" w:after="100"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="23"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph">
    <w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/><w:qFormat/>
    <w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>
  </w:style>
</w:styles>
"""


def _numbering_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="1">
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="-"/>
      <w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>
    </w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="1"/></w:num>
  <w:abstractNum w:abstractNumId="2">
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/>
      <w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>
    </w:lvl>
  </w:abstractNum>
  <w:num w:numId="2"><w:abstractNumId w:val="2"/></w:num>
</w:numbering>
"""
