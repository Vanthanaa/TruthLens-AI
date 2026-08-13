"""
metadata.py

Extracts metadata from uploaded image and video files for the
AI Deepfake Detection System.

Exposes:
    extract_metadata(file_path) -> dict

This module is intentionally kept independent of Flask so it can be
imported and called directly by the backend team (Gopika).
"""

import os
from PIL import Image
import cv2


# File extensions we treat as images vs videos
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


def extract_metadata(file_path):
    """
    Extract metadata from an image or video file.

    Args:
        file_path (str): Path to the uploaded file.

    Returns:
        dict: A predictable dictionary of metadata fields.
              Missing/unsupported fields are returned as None
              instead of crashing the app.

    Example return (video):
        {
            "file_name": "video.mp4",
            "file_size": "12.5 MB",
            "width": 1920,
            "height": 1080,
            "resolution": "1920x1080",
            "format": "MP4",
            "fps": 30,
            "duration": 25.4,
            "file_type": "video"
        }

    Example return (image):
        {
            "file_name": "photo.jpg",
            "file_size": "2.1 MB",
            "width": 1080,
            "height": 1080,
            "resolution": "1080x1080",
            "format": "JPEG",
            "fps": None,
            "duration": None,
            "file_type": "image"
        }
    """

    # Base structure — always returned, even if extraction partially fails.
    metadata = {
        "file_name": None,
        "file_size": None,
        "width": None,
        "height": None,
        "resolution": None,
        "format": None,
        "fps": None,
        "duration": None,
        "file_type": None,
    }

    # --- Basic file info (safe even if the file is unreadable) ---
    if not file_path or not os.path.exists(file_path):
        metadata["file_name"] = os.path.basename(file_path) if file_path else "unknown"
        metadata["file_size"] = "0 MB"
        return metadata

    metadata["file_name"] = os.path.basename(file_path)
    metadata["file_size"] = _get_file_size(file_path)

    ext = os.path.splitext(file_path)[1].lower()

    if ext in IMAGE_EXTENSIONS:
        metadata["file_type"] = "image"
        _extract_image_metadata(file_path, metadata)
    elif ext in VIDEO_EXTENSIONS:
        metadata["file_type"] = "video"
        _extract_video_metadata(file_path, metadata)
    else:
        # Unknown extension — still return the safe defaults above
        metadata["file_type"] = "unknown"
        metadata["format"] = ext.replace(".", "").upper() if ext else None

    return metadata


def _get_file_size(file_path):
    """Return human-readable file size (e.g. '12.5 MB')."""
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.2f} MB"
    except OSError:
        return None


def _extract_image_metadata(file_path, metadata):
    """Fill in width, height, resolution, and format for an image."""
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            metadata["width"] = width
            metadata["height"] = height
            metadata["resolution"] = f"{width}x{height}"
            metadata["format"] = img.format  # e.g. 'JPEG', 'PNG'
    except Exception as e:
        # Do not crash the whole app because one image couldn't be read
        print(f"[metadata.py] Warning: could not read image metadata: {e}")


def _extract_video_metadata(file_path, metadata):
    """Fill in width, height, resolution, format, fps, and duration for a video."""
    try:
        cap = cv2.VideoCapture(file_path)

        if not cap.isOpened():
            print(f"[metadata.py] Warning: could not open video file: {file_path}")
            return

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        metadata["width"] = width if width else None
        metadata["height"] = height if height else None
        metadata["resolution"] = f"{width}x{height}" if width and height else None
        metadata["fps"] = round(fps, 2) if fps else None

        if fps and frame_count:
            duration = frame_count / fps
            metadata["duration"] = round(duration, 2)

        ext = os.path.splitext(file_path)[1].replace(".", "").upper()
        metadata["format"] = ext

        cap.release()
    except Exception as e:
        print(f"[metadata.py] Warning: could not read video metadata: {e}")


# --- Quick manual test (run this file directly to sanity-check it) ---
if __name__ == "__main__":
    test_file = "sample.jpg"  # change this to a real file path to test
    result = extract_metadata(test_file)
    print(result)