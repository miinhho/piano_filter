from config import FilterConfig
from filter import PianoFilter


def main():
    """Main entry point"""
    # Create configuration
    config = FilterConfig(
        detection_threshold=0.001,  # Extremely sensitive - even low scores trigger
        reduced_volume=0.2,
        detection_history_size=15,  # Larger window for continuous piano playing
        restore_threshold=0.9,  # 90% non-detections needed to restore
        buffer_size=2048,
    )

    # Create and start filter
    piano_filter = PianoFilter(config)
    piano_filter.start()


if __name__ == "__main__":
    main()
