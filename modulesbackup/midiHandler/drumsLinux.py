import mido
import time
import random
import threading

from modules import configuration
from modules.functions import mainFunctions
from modules.midiHandler import midiLinux as sharedMidiLinux  # reuse uinput

pressedKeys = set()
heldKeys = set()
timerList = []
keyboardHandlers = []

stopEvent = threading.Event()
clockThreadRef = None
playThread = None
paused = False
closeThread = False
playbackSpeed = 1.0

log = mainFunctions.log

def press(key):
    sharedMidiLinux.press(key)
    heldKeys.add(str(key))

def release(key):
    sharedMidiLinux.release(key)
    heldKeys.discard(str(key))

def pressAndMaybeRelease(key):
    press(key)
    if configuration.configData["drumsMacro"]["customHoldLength"]["enabled"]:
        t = threading.Timer(configuration.configData["drumsMacro"]["customHoldLength"]["noteLength"], lambda: release(key))
        timerList.append(t)
        t.start()

def _drumsMap():
    dm = configuration.configData['drumsMacro']['drumsMap']
    return {
        42: dm['closed_Hi-Hat'],
        44: dm['closed_Hi-Hat2'],
        46: dm['open_Hi-Hat'],
        48: dm['tom1'],
        50: dm['tom1_2'],
        60: dm['tom'],
        62: dm['tom2_2'],
        49: dm['rightCrash'],
        55: dm['leftCrash'],
        38: dm['snare'],
        40: dm['snare2'],
        37: dm['snareSide'],
        35: dm['kick'],
        36: dm['kick2'],
        51: dm['ride'],
        53: dm['rideBell'],
        39: dm['cowbell'],
        52: dm['crashChina'],
        57: dm['splashCrash'],
        45: dm['lowTom'],
        47: dm['lowMidTom'],
    }

def parseMidi(message):
    drumsMap = _drumsMap()
    if message.type == 'note_on' and message.velocity > 0:
        key = drumsMap.get(message.note)
        if key is not None:
            pressAndMaybeRelease(key)
    elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
        key = drumsMap.get(message.note)
        if key is not None:
            release(key)

def playMidiOnce(filePath):
    mid = mido.MidiFile(filePath, clip=True)
    startTime = time.monotonic()
    currentTime = 0

    for msg in mid:
        if stopEvent.is_set() or closeThread:
            return False

        adjustedDelay = msg.time / playbackSpeed
        if configuration.configData["drumsMacro"]["randomFail"]["enabled"] and not msg.is_meta:
            if random.random() < configuration.configData["drumsMacro"]["randomFail"]["speed"] / 100:
                adjustedDelay *= random.uniform(0.5, 1.5)

        currentTime += adjustedDelay
        targetTime = startTime + currentTime

        while time.monotonic() < targetTime:
            if stopEvent.is_set() or closeThread:
                return False

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
            continue

        parseMidi(msg)

    return True

def playMidiFile(filePath):
    log("nanoMIDI Drums Translator (Linux/uinput)")
    log(f"Playing MIDI file: {filePath}")

    while not (stopEvent.is_set() or closeThread):
        finished = playMidiOnce(filePath)
        if not configuration.configData["drumsMacro"]["loopSong"] or not finished or stopEvent.is_set() or closeThread:
            break
        for k in list(heldKeys):
            release(k)

    if not configuration.configData["drumsMacro"]["loopSong"]:
        from modules.functions.drumsMacroFunctions import stopPlayback as stopPlaybackUI
        stopPlaybackUI()

def startPlayback(filePath, updateCallback=None):
    global playThread, clockThreadRef, closeThread, paused
    stopEvent.clear()
    closeThread = False
    paused = False
    if playThread and playThread.is_alive():
        return

    playThread = threading.Thread(target=playMidiFile, args=(filePath,), daemon=True)
    playThread.start()

def pausePlayback():
    global paused
    paused = not paused
    if paused and configuration.configData["drumsMacro"]["releaseOnPause"]:
        for k in list(heldKeys):
            release(k)
    log("Playback paused." if paused else "Playback resumed.")

def changeSpeed(amount):
    global playbackSpeed
    playbackSpeed = max(0.1, min(5.0, playbackSpeed + amount))
    log(f"Speed: {playbackSpeed * 100:.0f}%")

def stopPlayback():
    global closeThread, playThread, timerList
    if closeThread or stopEvent.is_set():
        return

    stopEvent.set()
    closeThread = True

    for k in list(heldKeys):
        try:
            release(k)
        except Exception:
            pass

    for t in list(timerList):
        try:
            t.cancel()
        except Exception:
            pass
    timerList.clear()

    if playThread and isinstance(playThread, threading.Thread):
        try:
            playThread.join(timeout=1.0)
        except Exception:
            pass

    log("Playback fully stopped.")
