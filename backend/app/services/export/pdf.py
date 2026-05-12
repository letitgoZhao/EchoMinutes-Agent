from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer

from app.services.export.markdown_blocks import MarkdownBlock, parse_markdown_blocks
from app.utils.logging import get_app_logger

logger = get_app_logger("export.pdf")

FONT_NAME = "EchoMinutesUnicode"
FALLBACK_FONT = "Helvetica"


def write_pdf_export(title: str, markdown: str, target_path: Path) -> None:
    font_name = _register_unicode_font()
    styles = _build_styles(font_name)
    story = _build_story(title, markdown, styles)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(target_path),
        pagesize=LETTER,
        rightMargin=0.72 * inch,
        leftMargin=0.72 * inch,
        topMargin=0.68 * inch,
        bottomMargin=0.68 * inch,
        title=title,
        author="EchoMinutes Agent",
        creator="EchoMinutes Agent",
        producer="EchoMinutes Agent",
    )
    document.build(story)


def _build_story(title: str, markdown: str, styles: dict[str, ParagraphStyle]) -> list[Flowable]:
    story: list[Flowable] = [
        Paragraph(_escape_paragraph(title), styles["title"]),
        Spacer(1, 0.18 * inch),
    ]

    for block in parse_markdown_blocks(markdown):
        story.extend(_block_to_flowables(block, styles))

    return story


def _block_to_flowables(
    block: MarkdownBlock,
    styles: dict[str, ParagraphStyle],
) -> list[Flowable]:
    if block.kind == "blank":
        return [Spacer(1, 0.08 * inch)]

    if block.kind == "heading":
        level = min(max(block.level, 1), 3)
        return [Paragraph(_escape_paragraph(block.text), styles[f"heading{level}"])]

    if block.kind == "bullet":
        return [Paragraph(_escape_paragraph(block.text), styles["bullet"], bulletText="-")]

    if block.kind == "numbered":
        return [
            Paragraph(
                _escape_paragraph(block.text),
                styles["numbered"],
                bulletText=f"{block.number}",
            )
        ]

    return [Paragraph(_escape_paragraph(block.text), styles["body"])]


def _build_styles(font_name: str) -> dict[str, ParagraphStyle]:
    base_styles = getSampleStyleSheet()
    text_color = colors.HexColor("#172126")
    muted_color = colors.HexColor("#44545b")

    body = ParagraphStyle(
        "EchoMinutesBody",
        parent=base_styles["BodyText"],
        alignment=TA_LEFT,
        fontName=font_name,
        fontSize=10.5,
        leading=15,
        textColor=text_color,
        spaceAfter=7,
        wordWrap="CJK",
    )
    title = ParagraphStyle(
        "EchoMinutesTitle",
        parent=body,
        fontSize=18,
        leading=24,
        spaceAfter=10,
    )

    return {
        "title": title,
        "heading1": ParagraphStyle(
            "EchoMinutesHeading1",
            parent=body,
            fontSize=16,
            leading=21,
            spaceBefore=8,
            spaceAfter=7,
        ),
        "heading2": ParagraphStyle(
            "EchoMinutesHeading2",
            parent=body,
            fontSize=14,
            leading=19,
            spaceBefore=7,
            spaceAfter=6,
        ),
        "heading3": ParagraphStyle(
            "EchoMinutesHeading3",
            parent=body,
            fontSize=12,
            leading=17,
            spaceBefore=6,
            spaceAfter=5,
            textColor=muted_color,
        ),
        "body": body,
        "bullet": ParagraphStyle(
            "EchoMinutesBullet",
            parent=body,
            leftIndent=18,
            firstLineIndent=0,
            bulletIndent=6,
        ),
        "numbered": ParagraphStyle(
            "EchoMinutesNumbered",
            parent=body,
            leftIndent=22,
            firstLineIndent=0,
            bulletIndent=4,
        ),
    }


def _register_unicode_font() -> str:
    registered_fonts = set(pdfmetrics.getRegisteredFontNames())
    if FONT_NAME in registered_fonts:
        return FONT_NAME

    for font_path in _unicode_font_candidates():
        if not font_path.exists():
            continue
        try:
            pdfmetrics.registerFont(TTFont(FONT_NAME, str(font_path)))
        except Exception as error:  # pragma: no cover - depends on host font files.
            logger.warning("Unable to register PDF font path=%s error=%s", font_path, error)
            continue

        logger.info("Registered PDF export font path=%s", font_path)
        return FONT_NAME

    logger.warning(
        "No usable Unicode desktop font found for PDF export; falling back to %s.",
        FALLBACK_FONT,
    )
    return FALLBACK_FONT


def _unicode_font_candidates() -> list[Path]:
    return [
        Path("C:/Windows/Fonts/msyh.ttf"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simsun.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/System/Library/Fonts/STHeiti Light.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]


def _escape_paragraph(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
