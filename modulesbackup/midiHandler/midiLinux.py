import re
import random
import threading
import time

import mido

from modules import configuration
from modules.functions import mainFunctions

# --- UINPUT ONLY (Wayland-safe) ---
from evdev import UInput, ecodes as e


log = mainFunctions.log

# ------------------------
# UINPUT DEVICE
# ------------------------

# Minimal key map needed by nanoMIDIPlayer mappings:
# - letters a-z
# - digits 0-9
# - modifiers: shift/ctrl/alt
# - space (sustain)
KEY_MAP = {
    **{chr(ord("a") + n): getattr(e, f"KEY_{chr(ord('A') + n)}") for n in range(26)},
    **{str(n): getattr(e, f"KEY_{n}") for n in range(10)},
    "space": e.KEY_SPACE,
    "shift": e.KEY_LEFTSHIFT,
    "ctrl": e.KEY_LEFTCTRL,
    "alt": e.KEY_LEFTALT,
}

# Create uinput device once. Expose only keys we use.
_ui = UInput({e.EV_KEY: list(set(KEY_MAP.values()))}, name="nanoMIDIPlayer-uinput", bustype=e.BUS_USB)

pressedKeys = set()     # for debug
heldKeys = set()        # keys currently held down (strings)
activeTransposedNotes = {}  # original_note -> [transposed_notes...]

stopEvent = threading.Event()
clockThreadRef = None
playThread = None
timerList = []

paused = False
closeThread = False
playbackSpeed = 1.0
sustainActive = False


# ------------------------
# LOW-LEVEL KEY I/O
# ------------------------

def _code(key):
    if key is None:
        return None
    return KEY_MAP.get(str(key).lower())


def press(key):
    """Press a mapped key once (idempotent if already held)."""
    code = _code(key)
    if code is None:
        return
    k = str(key).lower()
    if k in heldKeys:
        return
    _ui.write(e.EV_KEY, code, 1)
    _ui.syn()
    heldKeys.add(k)


def release(key):
    """Release a mapped key (idempotent if not held)."""
    code = _code(key)
    if code is None:
        return
    k = str(key).lower()
    if k not in heldKeys:
        return
    _ui.write(e.EV_KEY, code, 0)
    _ui.syn()
    heldKeys.discard(k)


def release_all():
    for k in list(heldKeys):
        release(k)


# ------------------------
# MIDI → KEY TRANSLATION
# ------------------------

_SPECIAL_SHIFTED = re.compile(r"[!@$%^*(]")  # how upstream encodes shifted number row in maps


def findVelocityKey(velocity: int) -> str:
    velocityMap = configuration.configData["midiPlayer"]["pianoMap"]["velocityMap"]
    thresholds = sorted(int(k) for k in velocityMap.keys())
    # binary-ish search like upstream
    minimum = 0
    maximum = len(thresholds) - 1
    index = 0
    while minimum <= maximum:
        index = (minimum + maximum) // 2
        if index == 0 or index == len(thresholds) - 1:
            break
        if thresholds[index] < velocity:
            minimum = index + 1
        else:
            maximum = index - 1
    return velocityMap[str(thresholds[index])]


def pressAndMaybeRelease(key: str):
    press(key)
    if configuration.configData["midiPlayer"]["customHoldLength"]["enabled"]:
        t = threading.Timer(
            configuration.configData["midiPlayer"]["customHoldLength"]["noteLength"],
            lambda: release(key),
        )
        timerList.append(t)
        t.start()


def _resolveMappedKey(note: int):
    allow88 = configuration.configData["midiPlayer"]["88Keys"]

    letterNoteMap = configuration.configData["midiPlayer"]["pianoMap"]["61keyMap"]
    lowNotes = configuration.configData["midiPlayer"]["pianoMap"]["88keyMap"]["lowNotes"]
    highNotes = configuration.configData["midiPlayer"]["pianoMap"]["88keyMap"]["highNotes"]

    note_s = str(note)

    if not allow88:
        if note_s not in letterNoteMap:
            return None, letterNoteMap
    else:
        if note_s not in letterNoteMap and note_s not in lowNotes and note_s not in highNotes:
            return None, letterNoteMap

    if note_s in letterNoteMap:
        return letterNoteMap[note_s], letterNoteMap
    if allow88 and note_s in lowNotes:
        return lowNotes[note_s], letterNoteMap
    if allow88 and note_s in highNotes:
        return highNotes[note_s], letterNoteMap

    return None, letterNoteMap


def simulateKey(msgType: str, note: int, velocity: int):
    key, letterNoteMap = _resolveMappedKey(note)
    if key is None:
        # keep log quiet for performance; uncomment if needed:
        # log(f"out of range: {note}")
        return

    # NOTE ON
    if msgType == "note_on":
        # velocity layer (Alt + velocityKey)
        if configuration.configData["midiPlayer"]["velocity"]:
            velocityKey = findVelocityKey(velocity)
            press("alt")
            press(velocityKey)
            release(velocityKey)
            release("alt")

        # Determine whether to use ctrl/shift logic like upstream
        if 36 <= note <= 96:
            # no doubles logic (prevents adjacent key overlap in some maps)
            if configuration.configData["midiPlayer"]["noDoubles"]:
                if _SPECIAL_SHIFTED.search(key):
                    # symbol keys represent "shift + previous note key"
                    release(letterNoteMap.get(str(note - 1), "").lower())
                else:
                    release(str(key).lower())

            if _SPECIAL_SHIFTED.search(key):
                # Represent shifted symbol by shift + previous key in map
                prev_key = letterNoteMap.get(str(note - 1))
                if prev_key:
                    press("shift")
                    pressAndMaybeRelease(prev_key)
                    release("shift")
            elif isinstance(key, str) and key.isupper():
                press("shift")
                pressAndMaybeRelease(key.lower())
                release("shift")
            else:
                pressAndMaybeRelease(key)
        else:
            # outside core range uses Ctrl modifier (octave shift in some games)
            release(str(key).lower())
            press("ctrl")
            pressAndMaybeRelease(str(key).lower())
            release("ctrl")

        return

    # NOTE OFF
    if msgType == "note_off":
        if 36 <= note <= 96:
            if _SPECIAL_SHIFTED.search(key):
                prev_key = letterNoteMap.get(str(note - 1))
                if prev_key:
                    release(prev_key)
            else:
                release(str(key).lower())
        else:
            release(str(key).lower())


def parseMidi(message):
    global sustainActive

    if message.type == "control_change" and configuration.configData["midiPlayer"]["sustain"]:
        if not sustainActive and message.value > configuration.configData["midiPlayer"]["sustainCutoff"]:
            sustainActive = True
            press("space")
        elif sustainActive and message.value < configuration.configData["midiPlayer"]["sustainCutoff"]:
            sustainActive = False
            release("space")
        return sustainActive

    if message.type in ("note_on", "note_off"):
        try:
            if message.velocity == 0:
                simulateKey("note_off", message.note, message.velocity)
            else:
                simulateKey(message.type, message.note, message.velocity)
        except IndexError:
            pass
    return sustainActive


# ------------------------
# PLAYBACK / TIMING
# ------------------------

def formatTime(seconds: float) -> str:
    seconds = max(0, int(seconds))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:0}:{minutes:02}:{secs:02}"


def clockThread(totalSeconds: float, updateCallback=None):
    """UI timestamp updater (matches upstream behavior)."""
    global closeThread, playbackSpeed, paused
    currentSeconds = 0

    while not (stopEvent.is_set() or closeThread):
        if not paused:
            shown = currentSeconds % max(1, int(totalSeconds))
            formattedTime = f"{formatTime(shown)} / {formatTime(totalSeconds)}"
            if configuration.configData["appUI"]["timestamp"]:
                if updateCallback:
                    updateCallback(formattedTime)
                else:
                    log(formattedTime)

            currentSeconds += 1
            for _ in range(10):
                if stopEvent.is_set() or closeThread:
                    break
                time.sleep(0.1 / max(0.1, playbackSpeed))
        else:
            time.sleep(0.1)


def playMidiOnce(midiFile: str):
    """Play once with pause-aware timing and upstream randomFail/transpose logic."""
    global sustainActive, paused

    mid = mido.MidiFile(midiFile, clip=True)
    startTime = time.monotonic()
    currentTime = 0
    wasPaused = False

    for msg in mid:
        if stopEvent.is_set() or closeThread:
            return False

        adjustedDelay = msg.time / max(0.1, playbackSpeed)

        # random fail (timing)
        if configuration.configData["midiPlayer"]["randomFail"]["enabled"] and not msg.is_meta:
            if random.random() < configuration.configData["midiPlayer"]["randomFail"]["speed"] / 100:
                adjustedDelay *= random.uniform(0.5, 1.5)

        currentTime += adjustedDelay
        targetTime = startTime + currentTime

        while time.monotonic() < targetTime:
            if stopEvent.is_set() or closeThread:
                return False

            # pause edge
            if paused and not wasPaused:
                wasPaused = True
                if configuration.configData["midiPlayer"]["releaseOnPause"]:
                    release_all()
                    if sustainActive:
                        release("space")
                        sustainActive = False

            if not paused and wasPaused:
                wasPaused = False

            # keep timeline correct while paused
            while paused and not (stopEvent.is_set() or closeThread):
                pauseStart = time.monotonic()
                time.sleep(0.05)
                pauseDuration = time.monotonic() - pauseStart
                startTime += pauseDuration
                targetTime += pauseDuration

            remaining = targetTime - time.monotonic()
            if remaining > 0:
                time.sleep(min(remaining, 0.005))

        if msg.is_meta:
            continue

        if paused:
            # preserve sustain state changes while paused like upstream
            if msg.type == "control_change" and msg.control == 64:
                if not configuration.configData["midiPlayer"]["sustain"]:
                    continue
                if msg.value > configuration.configData["midiPlayer"]["sustainCutoff"]:
                    sustainActive = True
                else:
                    sustainActive = False
            continue

        # random fail transpose (note_on only)
        if hasattr(msg, "note"):
            if msg.type == "note_on" and msg.velocity > 0:
                if (
                    configuration.configData["midiPlayer"]["randomFail"]["enabled"]
                    and random.random() < configuration.configData["midiPlayer"]["randomFail"]["transpose"] / 100
                ):
                    delta = random.randint(-12, 12)
                    newNote = msg.note + delta
                    activeTransposedNotes.setdefault(msg.note, []).append(newNote)

                    original = msg.note
                    msg.note = newNote
                    parseMidi(msg)
                    msg.note = original
                    continue

            # ensure note_off matches transposed note
            if msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in activeTransposedNotes and activeTransposedNotes[msg.note]:
                    transNote = activeTransposedNotes[msg.note].pop(0)
                    if not activeTransposedNotes[msg.note]:
                        del activeTransposedNotes[msg.note]

                    original = msg.note
                    msg.note = transNote
                    parseMidi(msg)
                    msg.note = original
                    continue

        parseMidi(msg)

    return True


def playMidiFile(midiFile: str):
    log("nanoMIDI — uinput mode")
    log(f"Playing MIDI file: {midiFile}")

    while not (stopEvent.is_set() or closeThread):
        finished = playMidiOnce(midiFile)
        if not configuration.configData["midiPlayer"]["loopSong"] or not finished or stopEvent.is_set() or closeThread:
            break
        release_all()

    # ensure UI is reset
    if not configuration.configData["midiPlayer"]["loopSong"]:
        from modules.functions.midiPlayerFunctions import stopPlayback
        stopPlayback()


def startPlayback(midiFile: str, updateCallback=None):
    global playThread, clockThreadRef, closeThread, paused

    stopEvent.clear()
    closeThread = False
    paused = False

    if playThread is not None and isinstance(playThread, threading.Thread) and playThread.is_alive():
        return

    totalSeconds = mido.MidiFile(midiFile, clip=True).length

    playThread = threading.Thread(target=playMidiFile, args=(midiFile,), daemon=True)
    clockThreadRef = threading.Thread(target=clockThread, args=(totalSeconds, updateCallback), daemon=True)
    clockThreadRef.start()
    playThread.start()


def pausePlayback():
    global paused, sustainActive
    paused = not paused

    if paused and configuration.configData["midiPlayer"]["releaseOnPause"]:
        release_all()
        if sustainActive:
            release("space")
            sustainActive = False

    log("Playback paused." if paused else "Playback resumed.")


def changeSpeed(amount: float):
    global playbackSpeed
    playbackSpeed = max(0.1, min(5.0, playbackSpeed + amount))
    log(f"Speed: {playbackSpeed * 100:.0f}%")


def stopPlayback():
    global closeThread, playThread, clockThreadRef, timerList, sustainActive

    if closeThread or stopEvent.is_set():
        return

    stopEvent.set()
    closeThread = True

    # cancel timers
    for t in list(timerList):
        try:
            t.cancel()
        except Exception:
            pass
    timerList.clear()

    # release all keys
    try:
        release_all()
        if sustainActive:
            release("space")
            sustainActive = False
    except Exception:
        pass

    # join threads (short)
    if playThread is not None and isinstance(playThread, threading.Thread):
        try:
            playThread.join(timeout=1.0)
        except Exception:
            pass

    if clockThreadRef is not None and isinstance(clockThreadRef, threading.Thread):
        try:
            clockThreadRef.join(timeout=1.0)
        except Exception:
            pass

    log("Playback fully stopped.")
