from pathlib import Path
import fitz  # PyMuPDF
import json


def extract_headings_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    font_stats = {}
    title = ""
    headings = []

    # Collect all fonts and their text spans
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if len(text) < 2:
                        continue
                    font_size = round(span["size"], 1)
                    font_stats.setdefault(font_size, []).append((text, page_num))

    # Sort fonts by size (descending)
    sorted_fonts = sorted(font_stats.items(), key=lambda x: -x[0])

    # Combine title from top two largest fonts on page 1
    if sorted_fonts:
        title_entries = sorted_fonts[0][1]
        if len(title_entries) >= 2 and title_entries[0][1] == title_entries[1][1] == 1:
            title = title_entries[0][0] + " " + title_entries[1][0]
        else:
            title = title_entries[0][0]

    # Use next few font sizes as H1, H2, H3
    heading_levels = sorted_fonts[1:4]
    level_names = ["H1", "H2", "H3"]
    for i, (size, entries) in enumerate(heading_levels):
        for text, page in entries:
            # Skip likely author names
            if i == 1 and page == 1 and len(text) < 25 and any(c in text for c in [".", ","]):
                continue
            # Skip too-short or too-generic H3s
            if i == 2 and len(text) <= 6:
                continue
            headings.append({
                "level": level_names[i],
                "text": text,
                "page": page
            })

    # Remove duplicate entries
    seen = set()
    final_headings = []
    for h in headings:
        key = (h['level'], h['text'])
        if key not in seen:
            seen.add(key)
            final_headings.append(h)

    return title, final_headings


def process_pdfs():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(exist_ok=True)

    for pdf_file in input_dir.glob("*.pdf"):
        print(f"Processing: {pdf_file.name}")
        title, outline = extract_headings_from_pdf(pdf_file)
        result = {
            "title": title,
            "outline": outline
        }
        with open(output_dir / f"{pdf_file.stem}.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)


if __name__ == "__main__":
    process_pdfs()
