import librosa
import numpy as np

videos = [
    "../test_videos/original.mp4",
    "../test_videos/deepfake.mp4"
]

for video in videos:
    print("\n==============================")
    print("VIDEO:", video)

    audio, sr = librosa.load(video, sr=16000, mono=True)

    print("Sample rate:", sr)
    print("Duration:", round(len(audio) / sr, 2), "seconds")

    # Mel-spectrogram
    mel = librosa.feature.melspectrogram(
        y=audio,
        sr=sr,
        n_mels=40
    )

    # Convert to log scale
    log_mel = librosa.power_to_db(mel, ref=np.max)

    print("FBank/Mel shape:", log_mel.shape)
    print("Audio extraction: SUCCESS")