"""Audio capture using sounddevice"""

import numpy as np
import sounddevice as sd


class AudioCapture:
    """Captures system audio using loopback device"""

    def __init__(self, sample_rate: int = 16000, buffer_size: int = 2048):
        """
        Initialize audio capture

        Args:
            sample_rate: Audio sample rate in Hz
            buffer_size: Audio buffer size for processing
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.loopback_device = None
        self.channels = 2

    def find_loopback_device(self) -> int | None:
        """
        Find loopback audio device

        Returns:
            Device index, or None if not found
        """
        devices = sd.query_devices()

        print("\n스캔한 오디오 장치:")
        print("-" * 60)
        for i, device in enumerate(devices):
            if device["max_input_channels"] > 0:  # type: ignore
                print(
                    f"[{i}] {device['name']} (입력 채널: {device['max_input_channels']})"  # type: ignore
                )
        print("-" * 60)

        # Look for loopback device
        for i, device in enumerate(devices):
            name_lower = device["name"].lower()  # type: ignore
            if any(
                keyword in name_lower
                for keyword in [
                    "loopback",
                    "stereo mix",
                    "스테레오 믹스",
                    "wave out",
                    "what u hear",
                ]
            ):
                if device["max_input_channels"] >= 1:  # type: ignore
                    return i

        # Fallback: find any input device
        print("\n⚠️  Loopback 장치를 찾을 수 없습니다!")
        print("\n해결 방법:")
        print("1. Windows 사운드 설정에서 'Stereo Mix' 활성화:")
        print("   - 작업 표시줄 스피커 아이콘 우클릭")
        print("   - '소리 설정 열기' → '사운드 제어판'")
        print("   - '녹음' 탭 → 빈 공간 우클릭")
        print("   - '사용 안 함 장치 표시' 체크")
        print("   - 'Stereo Mix' 또는 '스테레오 믹스' 우클릭 → '사용'")
        print("\n2. 또는 VB-CABLE 같은 가상 오디오 드라이버 설치")
        print("\n일단 기본 출력 장치로 시도합니다...")

        for i, device in enumerate(devices):
            if device["max_input_channels"] >= 2:  # type: ignore
                print(f"\n장치 사용 시도: {device['name']}")  # type: ignore
                return i

        return None

    def start_stream(self, callback):
        """
        Start audio input stream

        Args:
            callback: Callback function for audio data

        Returns:
            Context manager for audio stream
        """
        self.loopback_device = self.find_loopback_device()

        if self.loopback_device is None:
            raise Exception("사용 가능한 오디오 입력 장치가 없습니다.")

        devices = sd.query_devices()
        device_info = devices[self.loopback_device]  # type: ignore
        print(f"\n✓ 사용 장치: {device_info['name']}")

        self.channels = min(2, device_info["max_input_channels"])
        print(f"✓ 채널 수: {self.channels}")
        print(f"✓ 샘플레이트: {self.sample_rate}Hz")

        return sd.InputStream(
            device=self.loopback_device,
            channels=self.channels,
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            callback=callback,
        )

    @staticmethod
    def convert_to_mono(audio_data: np.ndarray) -> np.ndarray:
        """
        Convert stereo audio to mono

        Args:
            audio_data: Input audio data

        Returns:
            Mono audio data
        """
        if audio_data.shape[1] > 1:
            return np.mean(audio_data, axis=1)
        return audio_data[:, 0]
