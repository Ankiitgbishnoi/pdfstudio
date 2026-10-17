from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import io
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pdfstudio.cli import (
    merge_pdfs,
    split_pdf,
    rotate_pdf,
    extract_pages,
    watermark_pdf,
)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/merge", methods=["POST"])
def api_merge():
    files = request.files.getlist("files")
    if not files or len(files) < 2:
        return jsonify({"error": "Please upload at least 2 PDF files."}), 400

    pdf_paths = []
    for file in files:
        if not file.filename:
            continue
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "All files must be PDFs."}), 400
        name = secure_filename(file.filename)
        temp_path = os.path.join(tempfile.gettempdir(), f"upload_{os.urandom(8).hex()}_{name}")
        file.save(temp_path)
        pdf_paths.append(temp_path)

    if len(pdf_paths) < 2:
        return jsonify({"error": "At least 2 valid PDF files are required."}), 400

    output = os.path.join(tempfile.gettempdir(), f"merged_{os.urandom(8).hex()}.pdf")
    try:
        merge_pdfs(pdf_paths, output)
        return send_file(output, mimetype="application/pdf", as_attachment=True, download_name="merged.pdf")
    finally:
        for p in pdf_paths:
            if os.path.exists(p):
                os.remove(p)
        if os.path.exists(output):
            os.remove(output)


@app.route("/api/split", methods=["POST"])
def api_split():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "Please upload one PDF file."}), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "The uploaded file must be a PDF."}), 400

    temp_input = os.path.join(tempfile.gettempdir(), f"split_input_{os.urandom(8).hex()}.pdf")
    temp_dir = os.path.join(tempfile.gettempdir(), f"split_out_{os.urandom(8).hex()}")
    os.makedirs(temp_dir, exist_ok=True)
    file.save(temp_input)

    try:
        split_pdf(temp_input, temp_dir)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for entry in sorted(os.listdir(temp_dir)):
                if entry.lower().endswith(".pdf"):
                    full_path = os.path.join(temp_dir, entry)
                    zf.write(full_path, arcname=entry)
        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name="split_pages.zip")
    finally:
        for entry in sorted(os.listdir(temp_dir)) if os.path.exists(temp_dir) else []:
            os.remove(os.path.join(temp_dir, entry))
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        if os.path.exists(temp_input):
            os.remove(temp_input)


@app.route("/api/rotate", methods=["POST"])
def api_rotate():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "Please upload one PDF file."}), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "The uploaded file must be a PDF."}), 400

    degrees = request.form.get("degrees", "90")
    try:
        degrees = int(degrees)
    except ValueError:
        return jsonify({"error": "Degrees must be an integer."}), 400

    temp_input = os.path.join(tempfile.gettempdir(), f"rotate_input_{os.urandom(8).hex()}.pdf")
    temp_output = os.path.join(tempfile.gettempdir(), f"rotate_output_{os.urandom(8).hex()}.pdf")
    file.save(temp_input)

    try:
        rotate_pdf(temp_input, degrees, temp_output)
        return send_file(temp_output, mimetype="application/pdf", as_attachment=True, download_name="rotated.pdf")
    finally:
        if os.path.exists(temp_input):
            os.remove(temp_input)
        if os.path.exists(temp_output):
            os.remove(temp_output)


@app.route("/api/extract", methods=["POST"])
def api_extract():
    file = request.files.get("file")
    pages = request.form.get("pages", "1")
    if not file or not file.filename:
        return jsonify({"error": "Please upload one PDF file."}), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "The uploaded file must be a PDF."}), 400

    temp_input = os.path.join(tempfile.gettempdir(), f"extract_input_{os.urandom(8).hex()}.pdf")
    temp_output = os.path.join(tempfile.gettempdir(), f"extract_output_{os.urandom(8).hex()}.pdf")
    file.save(temp_input)

    try:
        extract_pages(temp_input, pages, temp_output)
        return send_file(temp_output, mimetype="application/pdf", as_attachment=True, download_name="extracted.pdf")
    finally:
        if os.path.exists(temp_input):
            os.remove(temp_input)
        if os.path.exists(temp_output):
            os.remove(temp_output)


@app.route("/api/watermark", methods=["POST"])
def api_watermark():
    file = request.files.get("file")
    text = request.form.get("text", "CONFIDENTIAL")
    if not file or not file.filename:
        return jsonify({"error": "Please upload one PDF file."}), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "The uploaded file must be a PDF."}), 400

    temp_input = os.path.join(tempfile.gettempdir(), f"watermark_input_{os.urandom(8).hex()}.pdf")
    temp_output = os.path.join(tempfile.gettempdir(), f"watermark_output_{os.urandom(8).hex()}.pdf")
    file.save(temp_input)

    try:
        watermark_pdf(temp_input, text, temp_output)
        return send_file(temp_output, mimetype="application/pdf", as_attachment=True, download_name="watermarked.pdf")
    finally:
        if os.path.exists(temp_input):
            os.remove(temp_input)
        if os.path.exists(temp_output):
            os.remove(temp_output)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
