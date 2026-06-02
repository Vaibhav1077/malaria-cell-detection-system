from __future__ import annotations

from pathlib import Path
import re
import textwrap


PAGE_WIDTH = 595
PAGE_HEIGHT = 842
LEFT = 54
TOP = 790
LINE_HEIGHT = 14
FONT_SIZE = 10
TITLE_SIZE = 18


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def clean_markdown_line(line: str) -> tuple[str, str]:
    stripped = line.strip()
    if stripped.startswith("# "):
        return "title", stripped[2:].strip()
    if stripped.startswith("## "):
        return "heading", stripped[3:].strip()
    if stripped.startswith("- "):
        return "bullet", stripped[2:].strip()
    if stripped.startswith("```"):
        return "code_fence", ""
    return "normal", stripped


def markdown_to_lines(markdown: str) -> list[tuple[str, str]]:
    output = []
    in_code = False
    for raw_line in markdown.splitlines():
        kind, text = clean_markdown_line(raw_line)
        if kind == "code_fence":
            in_code = not in_code
            continue
        if in_code:
            output.append(("code", raw_line.rstrip()))
            continue
        if text == "":
            output.append(("blank", ""))
            continue
        output.append((kind, text))
    return output


def wrap_items(items: list[tuple[str, str]]) -> list[tuple[str, str]]:
    wrapped = []
    for kind, text in items:
        if kind == "blank":
            wrapped.append((kind, text))
            continue
        width = 78
        prefix = ""
        if kind == "bullet":
            prefix = "- "
            width = 74
        if kind == "code":
            width = 86
        lines = textwrap.wrap(text, width=width) or [""]
        for index, line in enumerate(lines):
            if kind == "bullet":
                wrapped.append(("normal", f"{prefix if index == 0 else '  '}{line}"))
            else:
                wrapped.append((kind, line))
    return wrapped


def paginate(lines: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
    pages = []
    current = []
    y = TOP
    for kind, text in lines:
        decrement = LINE_HEIGHT
        if kind == "title":
            decrement = 28
        elif kind == "heading":
            decrement = 22
        elif kind == "blank":
            decrement = 9
        if y - decrement < 55:
            pages.append(current)
            current = []
            y = TOP
        current.append((kind, text))
        y -= decrement
    if current:
        pages.append(current)
    return pages


def page_stream(page_lines: list[tuple[str, str]], page_number: int) -> str:
    commands = ["BT"]
    y = TOP
    for kind, text in page_lines:
        if kind == "blank":
            y -= 9
            continue
        size = FONT_SIZE
        font = "F1"
        x = LEFT
        if kind == "title":
            size = TITLE_SIZE
            font = "F2"
        elif kind == "heading":
            size = 13
            font = "F2"
        elif kind == "code":
            size = 8
            font = "F3"
            x = LEFT + 10
        commands.append(f"/{font} {size} Tf")
        commands.append(f"1 0 0 1 {x} {y} Tm")
        commands.append(f"({escape_pdf_text(text)}) Tj")
        y -= 28 if kind == "title" else 20 if kind == "heading" else LINE_HEIGHT
    commands.append("/F1 8 Tf")
    commands.append(f"1 0 0 1 {PAGE_WIDTH - 90} 32 Tm")
    commands.append(f"(Page {page_number}) Tj")
    commands.append("ET")
    return "\n".join(commands)


def build_pdf(pages: list[list[tuple[str, str]]]) -> bytes:
    objects = []
    objects.append("<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{3 + i * 2} 0 R" for i in range(len(pages)))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>")

    for index, page in enumerate(pages):
        page_obj = 3 + index * 2
        content_obj = page_obj + 1
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> "
            f"/F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> "
            f"/F3 << /Type /Font /Subtype /Type1 /BaseFont /Courier >> >> >> "
            f"/Contents {content_obj} 0 R >>"
        )
        stream = page_stream(page, index + 1)
        stream_bytes = stream.encode("latin-1", errors="replace")
        objects.append(f"<< /Length {len(stream_bytes)} >>\nstream\n{stream}\nendstream")

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n{obj}\nendobj\n".encode("latin-1", errors="replace"))

    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("latin-1")
    )
    return bytes(pdf)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    markdown = (root / "PROJECT_REPORT.md").read_text(encoding="utf-8")
    markdown = re.sub(r"[–—]", "-", markdown)
    items = wrap_items(markdown_to_lines(markdown))
    pages = paginate(items)
    output = root / "Malaria_ML_Project_Report.pdf"
    output.write_bytes(build_pdf(pages))
    print(f"Created {output}")


if __name__ == "__main__":
    main()
