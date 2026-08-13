from flask import Blueprint, request, jsonify
import os

routes = Blueprint("routes", __name__)

UPLOAD_FOLDER = "uploads"


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