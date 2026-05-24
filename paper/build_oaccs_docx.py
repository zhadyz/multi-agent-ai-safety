"""Build OACCS position paper .docx by parsing OACCS_position_paper.md.

Single source of truth: the markdown file. This script parses it and
renders to .docx with professional military document formatting.
"""

import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import OxmlElement, parse_xml

PAPER_DIR = Path(__file__).resolve().parent
MD_SOURCE = PAPER_DIR / "OACCS_position_paper.md"
OUTPUT = PAPER_DIR / "OACCS_Multi_Agent_AI_Safety_Bari.docx"

NAVY = RGBColor(0, 51, 102)
NAVY_DARK = RGBColor(7, 55, 99)
DARK_GRAY = RGBColor(51, 51, 51)
MED_GRAY = RGBColor(128, 128, 128)
LIGHT_BG = "EEF4FB"
NAVY_HEX = "003366"
WHITE_HEX = "FFFFFF"
ALT_ROW = "F7F9FC"
HEADER_ROW = "003366"
BORDER = "D4DBE7"
BODY_FONT = "Aptos"
HEAD_FONT = "Aptos Display"
BODY_WIDTH_IN = 6.45

doc = Document()

# --- GLOBAL STYLES ---


def set_run_font(run, name=BODY_FONT):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)
    rfonts.set(qn("w:eastAsia"), name)
    rfonts.set(qn("w:cs"), name)


def set_style_font(doc_style, name):
    doc_style.font.name = name
    rpr = doc_style._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)
    rfonts.set(qn("w:eastAsia"), name)
    rfonts.set(qn("w:cs"), name)


style = doc.styles["Normal"]
set_style_font(style, BODY_FONT)
style.font.size = Pt(10.4)
style.font.color.rgb = DARK_GRAY
style.paragraph_format.space_after = Pt(5.5)
style.paragraph_format.space_before = Pt(0)
style.paragraph_format.line_spacing = 1.15

for hs in ["Heading 1", "Heading 2", "Heading 3"]:
    if hs in doc.styles:
        set_style_font(doc.styles[hs], HEAD_FONT)
        doc.styles[hs].font.color.rgb = NAVY

if "List Bullet" in doc.styles:
    bullet_style = doc.styles["List Bullet"]
    set_style_font(bullet_style, BODY_FONT)
    bullet_style.font.size = Pt(10.2)
    bullet_style.font.color.rgb = DARK_GRAY

for section in doc.sections:
    section.top_margin = Inches(0.76)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.92)
    section.right_margin = Inches(0.92)

    # Header
    header = section.header
    header.is_linked_to_previous = False
    hp = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hp.paragraph_format.space_after = Pt(0)
    hr = hp.add_run("UNCLASSIFIED")
    hr.bold = True
    hr.font.size = Pt(8)
    hr.font.color.rgb = RGBColor(0, 100, 0)
    set_run_font(hr)
    # Thin bottom border on header
    pPr = hp._element.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "4")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "008000")
    pBdr.append(bottom)
    pPr.append(pBdr)

    # Footer
    footer = section.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.space_before = Pt(4)
    # Top border on footer
    pPr2 = fp._element.get_or_add_pPr()
    pBdr2 = OxmlElement("w:pBdr")
    top_bdr = OxmlElement("w:top")
    top_bdr.set(qn("w:val"), "single")
    top_bdr.set(qn("w:sz"), "4")
    top_bdr.set(qn("w:space"), "1")
    top_bdr.set(qn("w:color"), "CCCCCC")
    pBdr2.append(top_bdr)
    pPr2.append(pBdr2)

    fr = fp.add_run("A1C Abdul Bari  |  147th CBCS, 195th Wing, CA ANG  |  OACCS 2026  |  Page ")
    fr.font.size = Pt(7.5)
    fr.font.color.rgb = MED_GRAY
    set_run_font(fr)
    # Page number field
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run_elem = fp.add_run()._element
    run_elem.append(fld_char1)
    run_elem.append(instr)
    run_elem.append(fld_char2)


# --- HELPERS ---

def add_rich_text(p, text):
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            run = p.add_run(part[2:-2])
            run.bold = True
            set_run_font(run)
        else:
            run = p.add_run(part)
            set_run_font(run)


def add_para(text):
    p = doc.add_paragraph()
    add_rich_text(p, text)
    p.paragraph_format.space_after = Pt(5.5)
    return p


def add_bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    add_rich_text(p, text)
    p.paragraph_format.space_after = Pt(4.5)
    return p


def shade_cell(cell, color_hex):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._element.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=90, start=120, bottom=90, end=120):
    tc_pr = cell._element.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in {"top": top, "start": start, "bottom": bottom, "end": end}.items():
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_cell_width(cell, width_in):
    cell.width = Inches(width_in)
    tc_pr = cell._element.get_or_add_tcPr()
    tc_w = tc_pr.tcW
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(int(width_in * 1440)))
    tc_w.set(qn("w:type"), "dxa")


def set_table_borders(table, color=BORDER, size="4"):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def set_table_fixed_layout(table):
    tbl_pr = table._tbl.tblPr
    layout = tbl_pr.first_child_found_in("w:tblLayout")
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")
    tbl_w = tbl_pr.first_child_found_in("w:tblW")
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(int(BODY_WIDTH_IN * 1440)))
    tbl_w.set(qn("w:type"), "dxa")


def infer_column_widths(headers, rows):
    ncols = len(headers)
    if ncols == 0:
        return []

    scores = []
    for ci, header in enumerate(headers):
        values = [header] + [row[ci] for row in rows if ci < len(row)]
        longest = max((len(v) for v in values), default=8)
        score = min(36, max(7, longest)) ** 0.72
        h = header.lower()
        if any(token in h for token in ["n ", "n(", "valid n", "rate", "year", "level", "id", "timeline"]):
            score *= 0.72
        if any(token in h for token in ["finding", "risk", "description", "interpretation", "evidence", "function"]):
            score *= 1.18
        scores.append(score)

    min_width = 0.58 if ncols >= 6 else 0.72
    remaining = BODY_WIDTH_IN - (min_width * ncols)
    total_score = sum(scores) or 1
    widths = [min_width + remaining * score / total_score for score in scores]
    return widths


def set_cell_font(cell, size=Pt(9), bold=False, color=None):
    for p in cell.paragraphs:
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.05
        for r in p.runs:
            r.font.size = size
            set_run_font(r)
            r.bold = bold
            if color:
                r.font.color.rgb = color


def add_table(header_line, row_lines):
    headers = [c.strip() for c in header_line.strip('|').split('|')]
    rows = []
    for rl in row_lines:
        cells = [c.strip() for c in rl.strip('|').split('|')]
        rows.append(cells)

    ncols = len(headers)
    table = doc.add_table(rows=1 + len(rows), cols=ncols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_fixed_layout(table)
    set_table_borders(table)
    widths = infer_column_widths(headers, rows)
    body_font_size = Pt(7.4 if ncols >= 6 else 8.1 if ncols >= 4 else 8.6)
    header_font_size = Pt(7.5 if ncols >= 6 else 8.0 if ncols >= 4 else 8.4)

    # Style header row: navy background, white text
    for ci, ht in enumerate(headers):
        cell = table.rows[0].cells[ci]
        cell.text = ht.replace('**', '')
        set_cell_width(cell, widths[ci])
        set_cell_margins(cell, top=105, start=115, bottom=105, end=115)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        shade_cell(cell, HEADER_ROW)
        set_cell_font(cell, size=header_font_size, bold=True, color=RGBColor(255, 255, 255))
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Style data rows with alternating shading
    for ri, row in enumerate(rows):
        for ci in range(min(len(row), ncols)):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = row[ci].replace('**', '')
            set_cell_width(cell, widths[ci])
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_font(cell, size=body_font_size)
            header = headers[ci].lower()
            if any(token in header for token in ["n", "rate", "timeline", "level", "threshold", "year", "status"]):
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if ri % 2 == 1:
                shade_cell(cell, ALT_ROW)

    # Remove excessive spacing after table
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(5)


def add_shaded_block(text):
    """Add a paragraph with light blue background shading."""
    p = doc.add_paragraph()
    add_rich_text(p, text)
    # Add shading to paragraph
    pPr = p._element.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), LIGHT_BG)
    pPr.append(shd)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.left_indent = Pt(8)
    p.paragraph_format.right_indent = Pt(6)
    p.paragraph_format.line_spacing = 1.12
    # Add left border for callout effect
    pBdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "24")
    left.set(qn("w:space"), "4")
    left.set(qn("w:color"), NAVY_HEX)
    pBdr.append(left)
    pPr.append(pBdr)
    for r in p.runs:
        r.font.size = Pt(10.0)
        set_run_font(r)
    return p


def add_separator():
    """Add a thin horizontal line."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    pPr = p._element.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "CCCCCC")
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_title_rule(color=NAVY_HEX, size="10"):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(10)
    pPr = p._element.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    top = OxmlElement("w:top")
    top.set(qn("w:val"), "single")
    top.set(qn("w:sz"), size)
    top.set(qn("w:space"), "1")
    top.set(qn("w:color"), color)
    pBdr.append(top)
    pPr.append(pBdr)


# --- PARSE AND BUILD ---

lines = MD_SOURCE.read_text(encoding="utf-8").splitlines()

is_bluf = False
is_monday = False
section_count = 0

i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()

    if not stripped:
        i += 1
        continue

    # Skip classification markers and horizontal rules
    if stripped == "UNCLASSIFIED":
        i += 1
        continue

    if stripped == "---":
        add_separator()
        i += 1
        continue

    # H1: # Title
    if stripped.startswith('# ') and not stripped.startswith('## '):
        text = stripped[2:]
        if i < 5:
            # Main title
            add_title_rule()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(22)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 0.95
            p.paragraph_format.keep_with_next = True
            run = p.add_run(text)
            run.bold = True
            run.font.size = Pt(21)
            run.font.color.rgb = NAVY_DARK
            set_run_font(run, HEAD_FONT)
        else:
            h = doc.add_heading(text, level=1)
            h.paragraph_format.space_before = Pt(18)
            h.paragraph_format.space_after = Pt(8)
            h.paragraph_format.keep_with_next = True
            for r in h.runs:
                r.font.size = Pt(14)
                r.font.color.rgb = NAVY
                set_run_font(r, HEAD_FONT)
            # Add bottom border to H1
            pPr = h._element.get_or_add_pPr()
            pBdr = OxmlElement("w:pBdr")
            bottom = OxmlElement("w:bottom")
            bottom.set(qn("w:val"), "single")
            bottom.set(qn("w:sz"), "8")
            bottom.set(qn("w:space"), "1")
            bottom.set(qn("w:color"), NAVY_HEX)
            pBdr.append(bottom)
            pPr.append(pBdr)
        i += 1
        continue

    # Subtitle line under the main title.
    if i < 8 and stripped.startswith('## '):
        text = stripped[3:]
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.italic = True
        run.font.size = Pt(12.4)
        run.font.color.rgb = RGBColor(69, 86, 108)
        set_run_font(run)
        i += 1
        continue

    # H2: ## Title
    if stripped.startswith('## ') and not stripped.startswith('### '):
        text = stripped[3:]
        section_count += 1

        # Page breaks before major sections
        if text.startswith('1. ') or text.startswith('5. ') or text.startswith('8. '):
            p = doc.add_paragraph()
            p.add_run().add_break(WD_BREAK.PAGE)

        # Track special sections
        is_bluf = text.startswith('BLUF')
        is_monday = text.startswith('What the 195th')

        h = doc.add_heading(text, level=2)
        h.paragraph_format.space_before = Pt(15)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        for r in h.runs:
            r.font.size = Pt(12.6)
            r.font.color.rgb = NAVY_DARK
            set_run_font(r, HEAD_FONT)
        i += 1
        continue

    # H3: ### Title
    if stripped.startswith('### '):
        text = stripped[4:]
        h = doc.add_heading(text, level=3)
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        for r in h.runs:
            r.font.size = Pt(10.9)
            r.font.color.rgb = RGBColor(0, 70, 130)
            set_run_font(r, HEAD_FONT)
        i += 1
        continue

    # Subtitle line (## under main title)
    if i < 8 and stripped.startswith('## ') and not any(c.isdigit() for c in stripped[:5]):
        text = stripped[3:]
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(8)
        run = p.add_run(text)
        run.italic = True
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(80, 80, 80)
        set_run_font(run)
        i += 1
        continue

    # Position Paper subtitle
    if stripped.startswith('**Position Paper'):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(stripped.replace('**', ''))
        run.italic = True
        run.font.size = Pt(9.5)
        run.font.color.rgb = MED_GRAY
        set_run_font(run)
        i += 1
        continue

    # Author line
    if stripped.startswith('A1C ') or stripped.startswith('147th '):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(stripped)
        run.font.size = Pt(9.8)
        run.font.color.rgb = DARK_GRAY
        set_run_font(run)
        i += 1
        continue

    # Tables
    if stripped.startswith('|') and '|' in stripped[1:]:
        header_line = stripped
        i += 1
        if i < len(lines) and re.match(r'^\|[\s\-:|]+\|$', lines[i].strip()):
            i += 1
        row_lines = []
        while i < len(lines) and lines[i].strip().startswith('|'):
            row_lines.append(lines[i].strip())
            i += 1
        add_table(header_line, row_lines)
        continue

    # Bullet points
    if stripped.startswith('- '):
        text = stripped[2:]
        add_bullet(text)
        i += 1
        continue

    # Numbered items
    if re.match(r'^\d+\.\s', stripped):
        # Use shaded callout for BLUF content and Monday Morning items
        if is_bluf or is_monday:
            add_shaded_block(stripped)
        else:
            add_para(stripped)
        i += 1
        continue

    # Italic footnote text
    if stripped.startswith('*') and stripped.endswith('*') and not stripped.startswith('**'):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        run = p.add_run(stripped[1:-1])
        run.italic = True
        run.font.size = Pt(8)
        run.font.color.rgb = MED_GRAY
        set_run_font(run)
        i += 1
        continue

    # Reference lines
    if re.match(r'^\[\d+\]', stripped):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.space_before = Pt(1)
        run = p.add_run(stripped)
        run.font.size = Pt(8)
        run.font.color.rgb = DARK_GRAY
        set_run_font(run)
        i += 1
        continue

    # BLUF paragraph gets shaded callout
    if is_bluf and not stripped.startswith('#') and not stripped.startswith('|') and not stripped.startswith('-'):
        add_shaded_block(stripped)
        i += 1
        continue

    # Keywords line
    if stripped.startswith('**Keywords:'):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        add_rich_text(p, stripped)
        for r in p.runs:
            r.font.size = Pt(9)
            r.font.color.rgb = MED_GRAY
            set_run_font(r)
        i += 1
        continue

    # Regular paragraph
    add_para(stripped)
    i += 1

# --- INSERT FIGURES ---
# Find the right locations and insert figures

def insert_figure_after_text(search_text, image_path, caption, width=Inches(5.5)):
    """Insert a figure after the paragraph containing search_text."""
    for pi, paragraph in enumerate(doc.paragraphs):
        if search_text in paragraph.text:
            # Add figure right after this paragraph
            # We need to add after — use the paragraph's element
            new_p = OxmlElement("w:p")
            new_r = OxmlElement("w:r")
            new_p.append(new_r)
            paragraph._element.addnext(new_p)

            # Create a proper paragraph for the image
            img_paragraph = doc.add_paragraph()
            img_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            img_paragraph.paragraph_format.space_before = Pt(8)
            img_paragraph.paragraph_format.space_after = Pt(3)
            img_paragraph.paragraph_format.keep_with_next = True
            run = img_paragraph.add_run()
            run.add_picture(str(image_path), width=width)

            # Add caption
            cap_p = doc.add_paragraph()
            cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap_p.paragraph_format.space_after = Pt(12)
            cap_p.paragraph_format.line_spacing = 1.05
            if ". " in caption:
                label, rest = caption.split(". ", 1)
                cap_label = cap_p.add_run(label + ". ")
                cap_label.bold = True
                cap_label.font.size = Pt(8.4)
                cap_label.font.color.rgb = NAVY_DARK
                set_run_font(cap_label)
                cap_r = cap_p.add_run(rest)
            else:
                cap_r = cap_p.add_run(caption)
            cap_r.italic = True
            cap_r.font.size = Pt(8.4)
            cap_r.font.color.rgb = MED_GRAY
            set_run_font(cap_r)

            # Move image paragraph and caption to right after search paragraph
            body = doc.element.body
            body.remove(img_paragraph._element)
            body.remove(cap_p._element)
            paragraph._element.addnext(cap_p._element)
            paragraph._element.addnext(img_paragraph._element)
            # Clean up the empty element we added
            body.remove(new_p)
            return True
    return False

figures = [
    {
        "file": "fig1_safety_matrix.png",
        "search": "The Safety Matrix: Architecture Harness",
        "caption": "Figure 1. Jailbreak success rate by model-interface pair and technique. "
                   "Green = low success (safer), red = high success (more vulnerable). "
                   "Rates reflect model-plus-interface safety, not isolated model alignment.",
        "width": Inches(6.1),
    },
    {
        "file": "fig1_technique_hierarchy.png",
        "search": "No Universal Safety Profile",
        "caption": "Figure 2. Technique profiles are model-specific. "
                   "Crossing lines show that neither vendor nor model size predicts a universal safety pattern.",
        "width": Inches(6.1),
    },
    {
        "file": "fig3_gpt55_temporal.png",
        "search": "Codex Zero-Output Refusals and Model Compliance",
        "caption": "Figure 3. GPT-5.5 temporal analysis. "
                   "Observed non-success is dominated by Codex zero-output behavior; when GPT-5.5 responded, it complied 99.6%.",
        "width": Inches(5.95),
    },
    {
        "file": "fig2_severity_distribution.png",
        "search": "Binary Coding Overstates Operational Risk",
        "caption": "Figure 4. Response severity distribution by model. "
                   "Among binary successes, 71% are educational/procedural and only 17% are actionable/exploit-level.",
        "width": Inches(6.1),
    },
    {
        "file": "fig4_factorial.png",
        "search": "Batch Presentation Increases Compliance on Sonnet",
        "caption": "Figure 5. Balanced 2x2 factorial on Sonnet decomposition. "
                   "Batch presentation averages 75.0% compliance versus 32.0% for sequential presentation (OR=6.4).",
        "width": Inches(5.75),
    },
]

for fig_info in figures:
    fig_path = PAPER_DIR / fig_info["file"]
    if fig_path.exists():
        inserted = insert_figure_after_text(
            fig_info["search"], fig_path, fig_info["caption"], fig_info["width"]
        )
        if inserted:
            print(f"  Inserted {fig_info['file']}")
        else:
            print(f"  Warning: anchor text not found for {fig_info['file']}")

doc.save(str(OUTPUT))
print(f"Saved: {OUTPUT}")
