from flask import Blueprint, request, jsonify
import os

from backend.complaints.complaint import save_complaint
from backend.reports.generate_pdf import generate_report

routes = Blueprint("routes", __name__)

UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "generated_reports"


# -------------------------
# Upload API
# -------------------------
@routes.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No file uploaded"
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    file.save(file_path)

    return jsonify({
        "success": True,
        "message": "File uploaded successfully",
        "filename": file.filename
    })


# -------------------------
# Complaint API
# -------------------------
@routes.route("/complaint", methods=["POST"])
def submit_complaint():

    complaint_data = request.get_json()

    if not complaint_data:
        return jsonify({
            "success": False,
            "message": "No complaint data provided"
        }), 400

    result = save_complaint(complaint_data)

    status_code = 200 if result["success"] else 400

    return jsonify(result), status_code


# -------------------------
# PDF Report API
# -------------------------
@routes.route("/report", methods=["POST"])
def create_report():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No report data provided"
        }), 400

    os.makedirs(REPORT_FOLDER, exist_ok=True)

    output_path = os.path.join(
        REPORT_FOLDER,
        "truthlens_report.pdf"
    )

    pdf_path = generate_report(
        data.get("metadata", {}),
        data.get("result", "Unknown"),
        data.get("confidence", 0),
        output_path,
        data.get("voice"),
        data.get("lip_sync")
    )

    return jsonify({
        "success": True,
        "message": "Report generated successfully",
        "pdf_path": pdf_path
    })