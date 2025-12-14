"""Volume controller using pycaw"""

from pycaw.pycaw import AudioUtilities


class VolumeController:
    """Controls system volume using Windows Core Audio API"""

    def __init__(self):
        self.volume_interface = None
        self.original_volume = 1.0
        self._initialize()

    def _initialize(self):
        """Initialize volume control interface"""
        try:
            speakers = AudioUtilities.GetSpeakers()
            if speakers is None:
                raise Exception("No speakers found")

            self.volume_interface = speakers.EndpointVolume
            print("✓ Volume control initialized (pycaw)")

            # Save original volume
            self.original_volume = self.get_volume()
            print(f"✓ Original volume saved: {self.original_volume * 100:.0f}%")

        except Exception as e:
            print(f"⚠️  Could not initialize volume control: {e}")
            print("⚠️  Volume control will be disabled")

    def set_volume(self, level: float) -> None:
        """
        Set system volume level

        Args:
            level: Volume level (0.0 to 1.0)
        """
        if not self.volume_interface:
            return

        try:
            self.volume_interface.SetMasterVolumeLevelScalar(level, None)
            print(f"[VOLUME] Set to {level * 100:.0f}%")
        except Exception as e:
            print(f"❌ Error setting volume: {e}")

    def get_volume(self) -> float:
        """
        Get current system volume level

        Returns:
            Current volume level (0.0 to 1.0)
        """
        if not self.volume_interface:
            return 1.0

        try:
            return self.volume_interface.GetMasterVolumeLevelScalar()
        except Exception as e:
            print(f"Error getting volume: {e}")
            return 1.0

    def restore_original_volume(self) -> None:
        """Restore the original volume level"""
        self.set_volume(self.original_volume)
