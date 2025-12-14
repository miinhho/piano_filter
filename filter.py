import threading
import time
from config import FilterConfig
from volume import VolumeController
from detection import YAMNetDetector
from state import State, StateMachine
from audio import AudioCapture


class PianoFilter:
    """Main piano filter orchestrator"""

    def __init__(self, config: FilterConfig):
        """
        Initialize piano filter

        Args:
            config: Filter configuration
        """
        self.config = config
        self.is_running = False

        # Initialize components
        self.volume_controller = VolumeController()
        self.detector = YAMNetDetector(
            sample_rate=config.sample_rate, piano_keywords=config.piano_keywords
        )
        self.state_machine = StateMachine(
            detection_threshold=config.detection_threshold,
            detection_history_size=config.detection_history_size,
            restore_threshold=config.restore_threshold,
        )
        self.audio_capture = AudioCapture(
            sample_rate=config.sample_rate, buffer_size=config.buffer_size
        )

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if status:
            print(f"Status: {status}")

        # Convert to mono
        audio_mono = AudioCapture.convert_to_mono(indata)

        # Process in separate thread
        audio_copy = audio_mono.copy()
        threading.Thread(
            target=self._process_chunk, args=(audio_copy,), daemon=True
        ).start()

    def _process_chunk(self, audio_chunk):
        """Process audio chunk"""
        # Calculate piano score
        piano_score = self.detector.calculate_score(audio_chunk)

        if piano_score is None:
            return

        # Always print status for debugging
        is_detected = piano_score > self.config.detection_threshold
        status = "🎹 DETECTED" if is_detected else "👂 listening"
        history_str = self.state_machine.get_detection_history_string()
        print(
            f"[{status}] Score: {piano_score:.3f} | History: {history_str} | State: {self.state_machine.state.value}",
            end="\r",
        )

        # Update state
        prev_state, new_state = self.state_machine.update(piano_score)

        # Handle state transitions
        if prev_state != new_state:
            if new_state == State.PIANO_DETECTED:
                print("\n🎹 Piano detected! Reducing volume...")
                self.volume_controller.set_volume(self.config.reduced_volume)
            elif new_state == State.NORMAL:
                print("\n🔊 Piano stopped. Restoring normal volume...")
                self.volume_controller.restore_original_volume()

    def start(self):
        """Start the piano filter"""
        print("\n" + "=" * 60)
        print("Piano Filter Started")
        print("=" * 60)
        print(f"Detection threshold: {self.config.detection_threshold}")
        print(f"Normal volume: {self.volume_controller.original_volume * 100:.0f}%")
        print(f"Reduced volume: {self.config.reduced_volume * 100:.0f}%")
        print(f"Detection history: {self.config.detection_history_size} samples")
        print(
            f"Restore threshold: {self.config.restore_threshold * 100:.0f}% non-detections"
        )
        print("=" * 60)
        print("\nListening to system audio...")
        print("Press Ctrl+C to stop\n")

        self.is_running = True

        try:
            with self.audio_capture.start_stream(self._audio_callback):
                print("\n🎧 모니터링 시작! (Ctrl+C로 종료)\n")
                while self.is_running:
                    time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\nStopping...")
        except Exception as e:
            print(f"\nError: {e}")
            print("\nTroubleshooting:")
            print("1. Enable 'Stereo Mix' in Windows Sound Settings")
            print("2. Or use virtual audio cable software (VB-CABLE, etc.)")
        finally:
            self.stop()

    def stop(self):
        """Stop the piano filter"""
        self.is_running = False
        print("\nRestoring normal volume...")
        self.volume_controller.restore_original_volume()
        print("Piano Filter stopped.")
