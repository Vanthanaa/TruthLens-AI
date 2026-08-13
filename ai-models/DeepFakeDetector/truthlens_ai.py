import cv2
import librosa
import numpy as np
import torch
from PIL import Image
from facenet_pytorch import MTCNN

from src.model import DeepfakeClassifier
from src.dataset import VAL_TRANSFORMS

MODEL_PATH = "checkpoints/best_model.pt"

device = torch.device("cpu")
mtcnn = MTCNN(
    image_size=224,
    margin=20,
    keep_all=False,
    device="cpu"
)

# -----------------------------
# Load visual model
# -----------------------------
model = DeepfakeClassifier(freeze_blocks=5)

model.load_state_dict(
    torch.load(
        MODEL_PATH,
        map_location=device,
        weights_only=True
    )
)

model.to(device)
model.eval()


# -----------------------------
# Visual analysis
# -----------------------------
def visual_score(video_path):
    cap = cv2.VideoCapture(video_path)

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total == 0:
        cap.release()
        return None

    indices = np.linspace(
        0,
        total - 1,
        15,
        dtype=int
    )

    scores = []

    for idx in indices:

        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))

        ret, frame = cap.read()

        if not ret:
            continue

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(frame)

        # Detect and crop the face
        face = mtcnn(image)

        if face is None:
            continue

        # MTCNN returns a normalized tensor
        # Convert it back to PIL so VAL_TRANSFORMS
        # can process it consistently.
        face_np = (
            (face.permute(1, 2, 0).numpy() + 1)
            / 2
            * 255
        ).clip(0, 255).astype(np.uint8)

        face_image = Image.fromarray(face_np)

        tensor = VAL_TRANSFORMS(
            face_image
        ).unsqueeze(0).to(device)

        with torch.no_grad():

            logit = model(tensor)

            probability = torch.sigmoid(
                logit
            ).item()

        scores.append(probability)

    cap.release()

    if not scores:
        return None

    return float(np.mean(scores))


# -----------------------------
# Audio feature extraction
# -----------------------------
def audio_features(video_path):

    audio, sr = librosa.load(
        video_path,
        sr=16000,
        mono=True
    )

    mel = librosa.feature.melspectrogram(
        y=audio,
        sr=sr,
        n_mels=40
    )

    log_mel = librosa.power_to_db(
        mel,
        ref=np.max
    )

    return log_mel


# -----------------------------
# TruthLens analysis
# -----------------------------
def analyze(video_path):

    print("\n================================")
    print("TRUTHLENS AI ANALYSIS")
    print("================================")

    print("\nVideo:")
    print(video_path)

    # Visual
    visual = visual_score(video_path)

    print("\nVisual analysis:")
    print(
        f"Fake probability: {visual:.2%}"
    )

    # Audio
    audio = audio_features(video_path)

    print("\nAudio analysis:")
    print(
        f"Sample rate: 16000 Hz"
    )

    print(
        f"FBank/Mel shape: {audio.shape}"
    )

    # Prototype fusion
    #
    # Audio classifier is not trained yet,
    # so we don't invent an audio probability.
    #
    # Current final score therefore remains
    # the visual baseline.

    final_score = visual

    label = (
        "FAKE"
        if final_score >= 0.5
        else "REAL"
    )

    print("\n================================")
    print("TRUTHLENS RESULT")
    print("================================")

    print(
        f"Visual score : {visual:.2%}"
    )

    print(
        "Audio branch : FEATURES EXTRACTED"
    )

    print(
        f"Final result : {label}"
    )

    print(
        f"Confidence   : {final_score:.2%}"
    )

    print("================================\n")


# -----------------------------
# Test videos
# -----------------------------

analyze("../test_videos/original.mp4")

analyze("../test_videos/deepfake.mp4")