#!/usr/bin/env python3
"""
PDF editing CLI for common tasks:
- merge multiple PDF files
- split a PDF into individual pages
- rotate pages
- extract a page range
- add a text watermark
"""

import argparse
import os
import tempfile

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas


def merge_pdfs(input_paths, output_path):
    if not input_paths:
        raise ValueError("No input PDFs supplied.")

    writer = PdfWriter()
    for input_path in input_paths:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input PDF not found: {input_path}")
        reader = PdfReader(input_path)
        for page in reader.pages:
            writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"Merged -> {output_path}")


def split_pdf(input_path, output_dir=None):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    out_dir = output_dir or os.getcwd()
    os.makedirs(out_dir, exist_ok=True)

    reader = PdfReader(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    for idx, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        output_path = os.path.join(out_dir, f"{base_name}_page{idx}.pdf")
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"Wrote {output_path}")


def rotate_pdf(input_path, degrees, output_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input PDF not found: {input_path}")
    if degrees % 90 != 0:
        raise ValueError("Rotation must be a multiple of 90 degrees.")

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        if degrees > 0:
            page.rotate_clockwise(degrees)
        elif degrees < 0:
            page.rotate_counter_clockwise(abs(degrees))
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"Rotated -> {output_path}")


def parse_page_spec(spec, page_count):
    indices = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue

        if "-" in part:
            start_text, end_text = part.split("-", 1)
            try:
                start = int(start_text)
                end = int(end_text)
            except ValueError as exc:
                raise ValueError(f"Invalid page range: '{part}'") from exc

            for page_num in range(start, end + 1):
                if 1 <= page_num <= page_count:
                    indices.append(page_num - 1)
        else:
            try:
                page_num = int(part)
            except ValueError as exc:
                raise ValueError(f"Invalid page number: '{part}'") from exc

            if 1 <= page_num <= page_count:
                indices.append(page_num - 1)

    return sorted(set(indices))


def extract_pages(input_path, page_spec, output_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    reader = PdfReader(input_path)
    page_indices = parse_page_spec(page_spec, len(reader.pages))
    if not page_indices:
        raise ValueError("No valid pages were selected from the requested page specification.")

    writer = PdfWriter()
    for idx in page_indices:
        writer.add_page(reader.pages[idx])

    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"Extracted -> {output_path}")


def make_watermark_pdf(text, width, height, watermark_path, font_size=48, opacity=0.18, angle=45):
    c = canvas.Canvas(watermark_path, pagesize=(width, height))
    c.setTitle("Watermark")
    c.setFillColor(Color(0, 0, 0))
    if hasattr(c, "setFillAlpha"):
        c.setFillAlpha(opacity)
    else:
        c.setFillColor(Color(0, 0, 0, alpha=opacity))

    c.saveState()
    c.translate(width / 2.0, height / 2.0)
    c.rotate(angle)
    c.setFont("Helvetica", font_size)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    c.showPage()
    c.save()


def watermark_pdf(input_path, text, output_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    reader = PdfReader(input_path)
    if not reader.pages:
        raise ValueError("The input PDF contains no pages.")

    first_page = reader.pages[0]
    media_box = first_page.mediabox
    width = float(media_box.width)
    height = float(media_box.height)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        watermark_path = tmp_file.name

    try:
        make_watermark_pdf(text, width, height, watermark_path)
        watermark_reader = PdfReader(watermark_path)
        watermarked_page = watermark_reader.pages[0]

        writer = PdfWriter()
        for page in reader.pages:
            merged_page = page
            merged_page.merge_page(watermarked_page)
            writer.add_page(merged_page)

        with open(output_path, "wb") as f:
            writer.write(f)

        print(f"Watermarked -> {output_path}")
    finally:
        if os.path.exists(watermark_path):
            os.remove(watermark_path)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="pdfstudio",
        description="Small PDF editing CLI for common PDF tasks.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    merge_parser = subparsers.add_parser("merge", help="Merge multiple PDFs into one file")
    merge_parser.add_argument("inputs", nargs="+", help="Input PDF files to merge")
    merge_parser.add_argument("-o", "--output", required=True, help="Output PDF path")

    split_parser = subparsers.add_parser("split", help="Split a PDF into a file per page")
    split_parser.add_argument("input", help="Input PDF")
    split_parser.add_argument("-d", "--out-dir", help="Directory for output files")

    rotate_parser = subparsers.add_parser("rotate", help="Rotate pages in a PDF")
    rotate_parser.add_argument("input", help="Input PDF")
    rotate_parser.add_argument("degrees", type=int, help="Rotation angle in degrees (90, 180, 270, or negative values)")
    rotate_parser.add_argument("-o", "--output", required=True, help="Output PDF path")

    extract_parser = subparsers.add_parser("extract", help="Extract a page range from a PDF")
    extract_parser.add_argument("input", help="Input PDF")
    extract_parser.add_argument("pages", help='Page specification such as "1,3-5"')
    extract_parser.add_argument("-o", "--output", required=True, help="Output PDF path")

    watermark_parser = subparsers.add_parser("watermark", help="Add a text watermark to each page")
    watermark_parser.add_argument("input", help="Input PDF")
    watermark_parser.add_argument("text", help="Watermark text")
    watermark_parser.add_argument("-o", "--output", required=True, help="Output PDF path")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "merge":
            merge_pdfs(args.inputs, args.output)
        elif args.command == "split":
            split_pdf(args.input, args.out_dir)
        elif args.command == "rotate":
            rotate_pdf(args.input, args.degrees, args.output)
        elif args.command == "extract":
            extract_pages(args.input, args.pages, args.output)
        elif args.command == "watermark":
            watermark_pdf(args.input, args.text, args.output)
        else:
            parser.print_help()
    except Exception as exc:
        print(f"Error: {exc}", file=os.sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
