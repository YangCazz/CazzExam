import sys, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def extract(pdf_path: str, out_dir: str | None = None) -> int:
    import pymupdf  # PyMuPDF
    doc = pymupdf.open(pdf_path)
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    out_dir = out_dir or os.path.join(os.path.dirname(os.path.abspath(pdf_path)), "txt")
    os.makedirs(out_dir, exist_ok=True)
    page_files = []
    for i, page in enumerate(doc):
        t = page.get_text()
        f = os.path.join(out_dir, f"{base}-p{i + 1}.txt")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(t)
        page_files.append(f)
    print(f"extracted {len(doc)} pages -> {out_dir}")
    return len(doc)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python pdf_extract.py <pdf_or_dir> [out_dir]")
        sys.exit(1)
    src = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else None
    if os.path.isdir(src):
        total = 0
        for f in sorted(glob.glob(os.path.join(src, "*.pdf"))):
            print("== ", os.path.basename(f))
            total += extract(f, out_dir)
        print("total pages:", total)
    else:
        extract(src, out_dir)
