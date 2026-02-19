class PlaybackState:
    def __init__(self):
        # runtime state
        self.running = False
        self.paused = False

        # UI speed (percent)
        self.speed = 100  

        # threads / control
        self.stop_event = None
        self.play_thread = None
        self.clock_thread = None

        # midi state
        self.sustain_active = False


# SINGLE GLOBAL INSTANCE
playback_state = PlaybackState()
