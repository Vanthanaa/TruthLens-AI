import cv2
import torch
import numpy as np
from PIL import Image

from src.model import DeepfakeClassifier
from src.dataset import VAL_TRANSFORMS

MODEL_PATH = "checkpoints/best_model.pt"

device = torch.device("cpu")

# Load model
model = DeepfakeClassifier(freeze_blocks=5)
model.load_state_dict(
    torch.load(MODEL_PATH, map_location=device, weights_only=True)
)
model.to(device)
model.eval()

def predict_video(video_path):
    cap = cv2.VideoCapture(video_path)

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total == 0:
        print("Could not read video.")
        return

    indices = np.linspace(0, total - 1, 15, dtype=int)

    predictions = []

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()

        if not ret:
            continue

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)

        image = image.resize((224, 224))
        tensor = VAL_TRANSFORMS(image).unsqueeze(0).to(device)

        with torch.no_grad():
            logit = model(tensor)
            probability = torch.sigmoid(logit).item()

        predictions.append(probability)

    cap.release()

    if not predictions:
        print("No frames could be analyzed.")
        return

    mean_probability = np.mean(predictions)

    label = "FAKE" if mean_probability >= 0.5 else "REAL"

    print("\n==============================")
    print("VIDEO:", video_path)
    print("PREDICTION:", label)
    print("FAKE PROBABILITY:", f"{mean_probability:.2%}")
    print("FRAMES ANALYZED:", len(predictions))
    print("==============================\n")


predict_video("../test_videos/original.mp4")
predict_video("../test_videos/deepfake.mp4")