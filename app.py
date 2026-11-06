"""
Flo Label Multiplier
Upload a shipping-label PDF (one label per page) and duplicate every page
N times in sequence:  L1, L1, L2, L2, L3, L3 ...
"""

import io
import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request, send_file
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

MAX_UPLOAD_MB = 50
MAX_QTY = 500

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


@app.route("/")
def index():
    return render_template("index.html", max_qty=MAX_QTY, max_mb=MAX_UPLOAD_MB)


@app.route("/healthz")
def healthz():
    return "ok", 200


@app.route("/process", methods=["POST"])
def process():
    # ---- Validate the file ----
    file = request.files.get("pdf")
    if file is None or file.filename == "":
        return jsonify(error="Please choose a PDF file."), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify(error="Only .pdf files are supported."), 400

    # ---- Validate the quantity ----
    try:
        qty = int(request.form.get("qty", "1"))
    except ValueError:
        return jsonify(error="Qty per label must be a whole number."), 400
    if qty < 1 or qty > MAX_QTY:
        return jsonify(error=f"Qty per label must be between 1 and {MAX_QTY}."), 400

    # ---- Read the PDF ----
    try:
        reader = PdfReader(io.BytesIO(file.read()))
        if reader.is_encrypted:
            # Many label PDFs are "encrypted" with an empty password; try that.
            if not reader.decrypt(""):
                return jsonify(error="This PDF is password-protected."), 400
        original_pages = len(reader.pages)
    except (PdfReadError, Exception):
        return jsonify(error="Could not read this PDF. Is the file valid?"), 400

    if original_pages == 0:
        return jsonify(error="The PDF has no pages."), 400

    # ---- Duplicate pages: L1 x qty, L2 x qty, ... ----
    writer = PdfWriter()
    for page in reader.pages:
        for _ in range(qty):
            writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    base = os.path.splitext(os.path.basename(file.filename))[0] or "labels"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_name = f"{base}_x{qty}_{stamp}.pdf"

    response = send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=download_name,
    )
    # Let the frontend show a summary
    response.headers["X-Original-Pages"] = str(original_pages)
    response.headers["X-Output-Pages"] = str(original_pages * qty)
    response.headers["X-Filename"] = download_name
    response.headers["Access-Control-Expose-Headers"] = (
        "X-Original-Pages, X-Output-Pages, X-Filename"
    )
    return response


@app.errorhandler(413)
def too_large(_e):
    return jsonify(error=f"File is too large. Max size is {MAX_UPLOAD_MB} MB."), 413


if __name__ == "__main__":
    # Local development only. Render uses gunicorn (see Start Command).
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
