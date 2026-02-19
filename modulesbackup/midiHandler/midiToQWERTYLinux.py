import re
import mido
import threading

from modules.functions import mainFunctions
from modules import configuration

from modules.midiHandler import midiLinux as sharedMidiLinux  # reuse uinput press/release logic

pressedKeys = set()
heldKeys = set()
activeTransposedNotes = {}

log = mainFunctions.log

inPort = None
midiThread = None

def press(key): 
    sharedMidiLinux.press(key)
    heldKeys.add(str(key))

def release(key):
    sharedMidiLinux.release(key)
    heldKeys.discard(str(key))

def findVelocityKey(velocity):
    velocityMap = configuration.configData["midiToQwerty"]["pianoMap"]["velocityMap"]
    thresholds = sorted(int(k) for k in velocityMap.keys())
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

def pressAndMaybeRelease(key):
    press(key)
    if configuration.configData["midiToQwerty"]["customHoldLength"]["enabled"]:
        t = threading.Timer(configuration.configData["midiToQwerty"]["customHoldLength"]["noteLength"], lambda: release(key))
        t.start()

def simulateKey(msgType, note, velocity):
    allow88 = configuration.configData["midiToQwerty"]["88Keys"]

    letterNoteMap = configuration.configData["midiToQwerty"]["pianoMap"]["61keyMap"]
    lowNotes = configuration.configData["midiToQwerty"]["pianoMap"]["88keyMap"]["lowNotes"]
    highNotes = configuration.configData["midiToQwerty"]["pianoMap"]["88keyMap"]["highNotes"]

    if not allow88:
        if str(note) not in letterNoteMap:
            return
    else:
        if str(note) not in letterNoteMap and str(note) not in lowNotes and str(note) not in highNotes:
            return

    if str(note) in letterNoteMap:
        key = letterNoteMap[str(note)]
    elif allow88 and str(note) in lowNotes:
        key = lowNotes[str(note)]
    elif allow88 and str(note) in highNotes:
        key = highNotes[str(note)]
    else:
        return

    if msgType == "note_on":
        if configuration.configData["midiToQwerty"]["velocity"]:
            velocityKey = findVelocityKey(velocity)
            press("alt")
            press(velocityKey)
            release(velocityKey)
            release("alt")

        if 36 <= note <= 96:
            if configuration.configData["midiToQwerty"]["noDoubles"]:
                if re.search(r"[!@$%^*(]", key):
                    release(letterNoteMap[str(note - 1)])
                else:
                    release(key.lower())

            if re.search(r"[!@$%^*(]", key):
                press("shift")
                pressAndMaybeRelease(letterNoteMap[str(note - 1)])
                release("shift")
            elif key.isupper():
                press("shift")
                pressAndMaybeRelease(key.lower())
                release("shift")
            else:
                pressAndMaybeRelease(key)
        else:
            release(key.lower())
            press("ctrl")
            pressAndMaybeRelease(key.lower())
            release("ctrl")

    elif msgType == "note_off":
        if 36 <= note <= 96:
            if re.search(r"[!@$%^*(]", key):
                release(letterNoteMap[str(note - 1)])
            else:
                release(key.lower())
        else:
            release(key.lower())

def parseMidi(message):
    if message.type in ("note_on", "note_off"):
        if message.velocity == 0:
            simulateKey("note_off", message.note, message.velocity)
        else:
            simulateKey(message.type, message.note, message.velocity)

def _midi_loop(deviceName):
    global inPort
    try:
        inPort = mido.open_input(deviceName)
        log(f"Listening MIDI input: {deviceName}")
        for msg in inPort:
            parseMidi(msg)
    except Exception as e:
        log(f"MIDI input error: {e}")
    finally:
        try:
            if inPort:
                inPort.close()
        except Exception:
            pass
        inPort = None

def startMidiInput(deviceName):
    global midiThread
    if midiThread and midiThread.is_alive():
        return
    midiThread = threading.Thread(target=_midi_loop, args=(deviceName,), daemon=True)
    midiThread.start()

def stopMidiInput():
    global inPort
    try:
        if inPort:
            inPort.close()
    except Exception:
        pass
