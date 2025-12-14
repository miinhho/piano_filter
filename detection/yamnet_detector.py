import numpy as np
import tensorflow_hub as hub
from collections import deque


class YAMNetDetector:
    """Detects piano sounds using YAMNet model"""

    def __init__(
        self, sample_rate: int = 16000, piano_keywords: list[str] | None = None
    ):
        """
        Initialize YAMNet detector

        Args:
            sample_rate: Audio sample rate in Hz
            piano_keywords: Keywords to match piano-related classes
        """
        self.sample_rate = sample_rate
        self.yamnet_samples = int(0.975 * sample_rate)  # YAMNet needs 0.975s
        self.piano_keywords = piano_keywords or ["piano", "keyboard"]

        # Audio buffer
        self.audio_buffer = deque(maxlen=self.yamnet_samples * 2)

        # Load model
        print("Loading YAMNet model...")
        self.model = hub.load("https://tfhub.dev/google/yamnet/1")

        # Load and filter class names
        self.class_names = self._load_class_names()
        self.piano_classes = self._get_piano_class_indices()

        print(
            f"Piano classes to detect: {[self.class_names[i] for i in self.piano_classes]}"
        )

    def _load_class_names(self) -> list[str]:
        """Load YAMNet class names from model"""
        class_map_path = self.model.class_map_path().numpy().decode("utf-8")  # type: ignore
        class_names = []

        with open(class_map_path) as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    class_names.append(parts[2])  # Display name

        return class_names

    def _get_piano_class_indices(self) -> list[int]:
        """Get indices of piano-related classes"""
        indices = []
        for i, name in enumerate(self.class_names):
            if any(keyword in name.lower() for keyword in self.piano_keywords):
                indices.append(i)
        return indices

    def calculate_score(self, audio_chunk: np.ndarray) -> float | None:
        """
        Calculate piano detection score from audio chunk

        Args:
            audio_chunk: Audio data as numpy array

        Returns:
            Piano detection score (0-1), or None if not enough data
        """
        # Add to buffer
        self.audio_buffer.extend(audio_chunk)

        # Need enough samples for YAMNet
        if len(self.audio_buffer) < self.yamnet_samples:
            return None

        # Get last N samples for YAMNet
        waveform = np.array(list(self.audio_buffer)[-self.yamnet_samples :])
        waveform = waveform.astype(np.float32)

        # Run YAMNet
        scores, _, _ = self.model(waveform)  # type: ignore
        scores = scores.numpy()

        # Check piano classes
        max_piano_score = 0.0
        for piano_idx in self.piano_classes:
            piano_score = np.mean(scores[:, piano_idx])
            max_piano_score = max(max_piano_score, piano_score)

        return float(max_piano_score)
