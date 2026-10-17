# pdfstudio

A lightweight PDF editing tool for common operations such as merging, splitting, rotating, extracting pages, and stamping a text watermark.

## Features
- Merge multiple PDFs into one
- Split a PDF into one file per page
- Rotate pages by 90-degree increments
- Extract a page range (for example: `1,3-5`)
- Add a text watermark to each page
- Web UI for browser-based PDF edits

## CLI Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

## CLI Usage

### Merge PDFs
```bash
pdf-studio merge a.pdf b.pdf -o merged.pdf
```

### Split PDF
```bash
pdf-studio split large.pdf -d output_folder
```

### Rotate PDF
```bash
pdf-studio rotate input.pdf 90 -o rotated.pdf
```

### Extract pages
```bash
pdf-studio extract input.pdf "1,3-5" -o extracted.pdf
```

### Add watermark
```bash
pdf-studio watermark input.pdf "CONFIDENTIAL" -o watermarked.pdf
```

## Web UI (React + Flask)

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
export FLASK_DEBUG=1
flask run --host 0.0.0.0 --port 5000
```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Then open the local frontend URL shown in the terminal (typically http://localhost:5173).

## Docker (optional)

```bash
docker compose up --build
```

## Notes
This project is designed as a simple CLI-focused MVP and a browser-based editor for common PDF operations. For visual editing, annotation, OCR, or redaction, a more advanced PDF workflow or a GUI-based tool is recommended.
