class PlaybackState:
    def __init__(self):
        self.running = False
        self.paused = False
        self.speed = 1.0

        self.stop_event = None
        self.play_thread = None
        self.clock_thread = None

        self.sustain_active = False


# SINGLE GLOBAL INSTANCE
playback_state = PlaybackState()
