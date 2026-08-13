"""
complaints/complaint.py

Handles complaint submission for the AI Deepfake Detection System.

Exposes:
    save_complaint(complaint_data) -> dict

Complaints are currently stored in a simple JSON file
(complaints_data/complaints.json). The storage logic is isolated in
its own functions so it can later be swapped for a database without
changing how the rest of the app calls save_complaint().

This module is intentionally kept independent of Flask so it can be
imported and called directly by the backend team (Gopika).
"""

import os
import re
import json
from datetime import datetime


# --- Configuration ---
COMPLAINTS_DIR = "complaints_data"
COMPLAINTS_FILE = os.path.join(COMPLAINTS_DIR, "complaints.json")

REQUIRED_FIELDS = ["name", "email", "phone", "description"]

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^\d{10}$")


def save_complaint(complaint_data):
    """
    Validate, store, and return a unique ID for a new complaint.

    Args:
        complaint_data (dict): Expected keys:
            name (str)
            email (str)
            phone (str)
            description (str)

    Returns:
        dict: On success:
            {
                "success": True,
                "complaint_id": "CMP2026001",
                "message": "Complaint submitted successfully"
            }
        On failure:
            {
                "success": False,
                "complaint_id": None,
                "message": "<reason for failure>"
            }
    """

    if not complaint_data or not isinstance(complaint_data, dict):
        return _failure("Complaint data must be a valid dictionary.")

    # --- Validate required fields ---
    is_valid, error_message = _validate_complaint(complaint_data)
    if not is_valid:
        return _failure(error_message)

    # --- Build the record to store ---
    existing_complaints = _load_complaints()
    complaint_id = _generate_complaint_id(existing_complaints)

    record = {
        "complaint_id": complaint_id,
        "name": complaint_data["name"].strip(),
        "email": complaint_data["email"].strip(),
        "phone": complaint_data["phone"].strip(),
        "description": complaint_data["description"].strip(),
        "submitted_at": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
    }

    # --- Save ---
    try:
        existing_complaints.append(record)
        _write_complaints(existing_complaints)
    except Exception as e:
        return _failure(f"Could not save complaint: {e}")

    return {
        "success": True,
        "complaint_id": complaint_id,
        "message": "Complaint submitted successfully",
    }


def _validate_complaint(complaint_data):
    """Check required fields are present and reasonably well-formed."""

    for field in REQUIRED_FIELDS:
        value = complaint_data.get(field)
        if value is None or not str(value).strip():
            return False, f"Missing required field: '{field}'"

    email = str(complaint_data["email"]).strip()
    if not EMAIL_REGEX.match(email):
        return False, "Invalid email format."

    phone = str(complaint_data["phone"]).strip()
    if not PHONE_REGEX.match(phone):
        return False, "Phone number must be exactly 10 digits."

    return True, None


def _generate_complaint_id(existing_complaints):
    """
    Generate the next complaint ID in the form CMP<year><3-digit-seq>.

    Example: CMP2026001, CMP2026002, ...
    Sequence resets naturally per year since it's based on count of
    complaints already logged for the current year.
    """
    year = datetime.now().year
    prefix = f"CMP{year}"

    # Count how many complaints already exist for this year
    count_this_year = sum(
        1 for c in existing_complaints
        if c.get("complaint_id", "").startswith(prefix)
    )

    next_number = count_this_year + 1
    return f"{prefix}{next_number:03d}"


def _load_complaints():
    """Load existing complaints from the JSON file. Returns a list."""
    if not os.path.exists(COMPLAINTS_FILE):
        return []

    try:
        with open(COMPLAINTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        # Corrupted or unreadable file — start fresh rather than crash
        return []


def _write_complaints(complaints):
    """Write the full list of complaints back to the JSON file."""
    os.makedirs(COMPLAINTS_DIR, exist_ok=True)
    with open(COMPLAINTS_FILE, "w", encoding="utf-8") as f:
        json.dump(complaints, f, indent=4)


def _failure(message):
    return {
        "success": False,
        "complaint_id": None,
        "message": message,
    }


# --- Quick manual test (run this file directly to sanity-check it) ---
if __name__ == "__main__":
    sample_complaint = {
        "name": "User Name",
        "email": "user@example.com",
        "phone": "9876543210",
        "description": "This video appears to be manipulated.",
    }

    result = save_complaint(sample_complaint)
    print(result)

    # Try an invalid one to confirm validation works
    bad_complaint = {
        "name": "Someone",
        "email": "not-an-email",
        "phone": "123",
        "description": "",
    }
    print(save_complaint(bad_complaint))