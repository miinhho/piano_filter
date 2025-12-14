from dataclasses import dataclass


@dataclass
class FilterConfig:
    """Configuration for piano filter"""

    # Detection settings
    detection_threshold: float = 0.25
    detection_history_size: int = 10
    restore_threshold: float = 0.8

    # Volume settings
    reduced_volume: float = 0.2

    # Audio settings
    sample_rate: int = 16000
    buffer_size: int = 2048

    # Detection keywords
    piano_keywords: list[str] | None = None

    def __post_init__(self):
        if self.piano_keywords is None:
            self.piano_keywords = ["piano"]
