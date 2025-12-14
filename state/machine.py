"""State machine for piano filter"""

import threading
from enum import Enum
from collections import deque


class State(Enum):
    """State machine states"""

    NORMAL = "normal"
    PIANO_DETECTED = "piano_detected"


class StateMachine:
    """Manages state transitions based on detection history"""

    def __init__(
        self,
        detection_threshold: float,
        detection_history_size: int,
        restore_threshold: float,
    ):
        """
        Initialize state machine

        Args:
            detection_threshold: Threshold for piano detection
            detection_history_size: Number of recent detections to track
            restore_threshold: Ratio of non-detections needed to restore
        """
        self.detection_threshold = detection_threshold
        self.detection_history_size = detection_history_size
        self.restore_threshold = restore_threshold

        self.state = State.NORMAL
        self.lock = threading.Lock()
        self.detection_history = deque(maxlen=detection_history_size)

    def _is_piano_currently_playing(self) -> bool:
        """
        Check if piano is currently playing based on detection history

        Returns:
            True if piano is likely playing
        """
        if len(self.detection_history) < self.detection_history_size:
            return self.state == State.PIANO_DETECTED

        detection_count = sum(self.detection_history)
        detection_ratio = detection_count / len(self.detection_history)

        # Piano is playing if detection ratio is above (1 - restore_threshold)
        # e.g., restore_threshold=0.8 means we need 80% non-detections to restore
        # So we need detection_ratio < 0.2 to NOT be playing
        # Therefore, piano IS playing if detection_ratio >= 0.2
        return detection_ratio >= (1.0 - self.restore_threshold)

    def update(self, piano_score: float | None) -> tuple[State, State]:
        """
        Update state based on piano score

        Args:
            piano_score: Piano detection score (0-1), or None if not enough data

        Returns:
            Tuple of (previous_state, new_state)
        """
        if piano_score is None:
            return (self.state, self.state)

        # Add to detection history
        is_detected = piano_score > self.detection_threshold
        self.detection_history.append(is_detected)

        with self.lock:
            prev_state = self.state
            piano_playing = self._is_piano_currently_playing()

            if piano_playing and self.state == State.NORMAL:
                self.state = State.PIANO_DETECTED
            elif not piano_playing and self.state == State.PIANO_DETECTED:
                self.state = State.NORMAL

            return (prev_state, self.state)

    def get_detection_history_string(self) -> str:
        """Get visual representation of detection history"""
        return "".join(["█" if d else "░" for d in self.detection_history])
