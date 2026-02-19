import threading
import os
import platform
import datetime
import logging

import customtkinter
from tkinter import filedialog
from mido import MidiFile

from modules import configuration
from modules.playback_state import playback_state
from modules.functions import mainFunctions
from modules.midiHandler import useOutput

from ui.midiPlayer import MidiPlayerTab
from ui import customTheme

logger = logging.getLogger(__name__)
osName = platform.system()

# Pick platform handler (macro/uinput mode uses this)
if osName == "Windows":
    from modules.midiHandler import midiWindows as midiHandler
elif osName == "Darwin":
    from modules.midiHandler import midiDarwin as midiHandler
elif osName == "Linux":
    from modules.midiHandler import midiLinux as midiHandler

app = mainFunctions.getApp()

# ------------------------
# UI STATE VARS
# ------------------------
switchUseMIDIvar = customtkinter.StringVar(value="off")
switchSustainvar = customtkinter.StringVar(value="off")
switchNoDoublesvar = customtkinter.StringVar(value="off")
switchVelocityvar = customtkinter.StringVar(value="off")
switch88Keysvar = customtkinter.StringVar(value="off")

switchUseMIDIvar.set("on" if configuration.configData.get("midiPlayer", {}).get("useMIDIOutput", False) else "off")
switchSustainvar.set("on" if configuration.configData.get("midiPlayer", {}).get("sustain", False) else "off")
switchNoDoublesvar.set("on" if configuration.configData.get("midiPlayer", {}).get("noDoubles", False) else "off")
switchVelocityvar.set("on" if configuration.configData.get("midiPlayer", {}).get("velocity", False) else "off")
switch88Keysvar.set("on" if configuration.configData.get("midiPlayer", {}).get("88Keys", False) else "off")


# ------------------------
# CONFIG TOGGLES
# ------------------------
def switchUseMIDI():
    logger.info("switchUseMIDI called")
    try:
        configuration.configData["midiPlayer"]["useMIDIOutput"] = (switchUseMIDIvar.get() == "on")
        configuration.configData.save()

        mainFunctions.clearConsole()
        mainFunctions.refreshOutputDevices()

        if switchUseMIDIvar.get() == "on":
            threading.Thread(
                target=mainFunctions.insertConsoleText,
                args=("-------< WARNING >-------   This will not press keys for you!", True),
                daemon=True
            ).start()
        else:
            threading.Thread(
                target=mainFunctions.insertConsoleText,
                args=("Macro Mode.", True),
                daemon=True
            ).start()
    except Exception as e:
        logger.exception(f"switchUseMIDI error: {e}")


def switchSustain():
    logger.info("switchSustain called")
    try:
        configuration.configData["midiPlayer"]["sustain"] = (switchSustainvar.get() == "on")
        configuration.configData.save()
    except Exception as e:
        logger.exception(f"switchSustain error: {e}")


def switchNoDoubles():
    logger.info("switchNoDoubles called")
    try:
        configuration.configData["midiPlayer"]["noDoubles"] = (switchNoDoublesvar.get() == "on")
        configuration.configData.save()
    except Exception as e:
        logger.exception(f"switchNoDoubles error: {e}")


def switchVelocity():
    logger.info("switchVelocity called")
    try:
        configuration.configData["midiPlayer"]["velocity"] = (switchVelocityvar.get() == "on")
        configuration.configData.save()
    except Exception as e:
        logger.exception(f"switchVelocity error: {e}")


def switch88Keys():
    logger.info("switch88Keys called")
    try:
        configuration.configData["midiPlayer"]["88Keys"] = (switch88Keysvar.get() == "on")
        configuration.configData.save()
    except Exception as e:
        logger.exception(f"switch88Keys error: {e}")


# ------------------------
# FILE PICKER / SAVED FILES
# ------------------------
def selectFile():
    logger.info("selectFile called")
    try:
        MidiPlayerTab.filePathEntry.set("")
        unbindControls()
        stopPlayback()

        MidiPlayerTab.timelineIndicator.configure(text="0:00:00 / 0:00:00")
        MidiPlayerTab.playButton.configure(text="Play")

        filePath = filedialog.askopenfilename(filetypes=[("MIDI files", "*.mid"), ("MIDI files", "*.midi")])
        logger.debug(f"filePath selected: {filePath}")

        if not filePath:
            return

        currentVAL = list(MidiPlayerTab.filePathEntry.cget("values"))
        if filePath not in currentVAL:
            currentVAL.append(filePath)
            MidiPlayerTab.filePathEntry.configure(values=currentVAL)

        MidiPlayerTab.filePathEntry.set(filePath)
        midiFile = MidiFile(filePath, clip=True)

        total = midiFile.length
        timelineText = (
            f"0:00:00 / {str(datetime.timedelta(seconds=int(total)))}"
            if configuration.configData["appUI"]["timestamp"]
            else f"X:XX:XX / {str(datetime.timedelta(seconds=int(total)))}"
        )
        MidiPlayerTab.timelineIndicator.configure(text=timelineText)

        configuration.configData["midiPlayer"]["currentFile"] = filePath
        configuration.configData["midiPlayer"].setdefault("midiList", [])
        if filePath not in configuration.configData["midiPlayer"]["midiList"]:
            configuration.configData["midiPlayer"]["midiList"].append(filePath)
        configuration.configData.save()

        bindControls()
    except Exception as e:
        logger.exception(f"selectFile error: {e}")


def loadSavedFile():
    logger.info("loadSavedFile called")
    try:
        midiList = configuration.configData["midiPlayer"].get("midiList", [])
        currentFile = configuration.configData["midiPlayer"].get("currentFile", "")

        midiList = [f for f in midiList if os.path.exists(f)]
        configuration.configData["midiPlayer"]["midiList"] = midiList

        if currentFile and not os.path.exists(currentFile):
            currentFile = ""
            configuration.configData["midiPlayer"]["currentFile"] = ""

        configuration.configData.save()

        entryValues = list(MidiPlayerTab.filePathEntry.cget("values"))

        downloadFolder = os.path.join(configuration.baseDirectory, "Midis")
        if os.path.exists(downloadFolder):
            for filename in os.listdir(downloadFolder):
                if filename.lower().endswith((".mid", ".midi")):
                    fp = os.path.join(downloadFolder, filename)
                    if fp not in entryValues and fp not in midiList:
                        entryValues.append(fp)

        for p in midiList:
            if p not in entryValues:
                entryValues.append(p)

        MidiPlayerTab.filePathEntry.configure(values=entryValues)

        chosen = None
        if currentFile:
            chosen = currentFile
        elif midiList:
            chosen = midiList[0]

        if chosen:
            if chosen not in entryValues:
                entryValues.append(chosen)
                MidiPlayerTab.filePathEntry.configure(values=entryValues)
            MidiPlayerTab.filePathEntry.set(chosen)

            configuration.configData["midiPlayer"]["currentFile"] = chosen
            configuration.configData.save()

            midiFileData = MidiFile(chosen, clip=True)
            total = midiFileData.length
            timelineText = (
                f"0:00:00 / {str(datetime.timedelta(seconds=int(total)))}"
                if configuration.configData["appUI"]["timestamp"]
                else f"X:XX:XX / {str(datetime.timedelta(seconds=int(total)))}"
            )
            MidiPlayerTab.timelineIndicator.configure(text=timelineText)
            logger.debug(f"loaded file: {chosen}")
            return

        MidiPlayerTab.filePathEntry.set("None")
        MidiPlayerTab.timelineIndicator.configure(text="0:00:00 / 0:00:00")
        logger.debug("no saved files found")
    except Exception as e:
        logger.exception(f"loadSavedFile error: {e}")


def switchMidiEvent(event=None):
    logger.info("switchMidiEvent called")
    try:
        midiFile = MidiPlayerTab.filePathEntry.get()
        configuration.configData["midiPlayer"]["currentFile"] = midiFile
        configuration.configData.save()

        midiFileData = MidiFile(midiFile, clip=True)
        total = midiFileData.length
        timelineText = (
            f"0:00:00 / {str(datetime.timedelta(seconds=int(total)))}"
            if configuration.configData["appUI"]["timestamp"]
            else f"X:XX:XX / {str(datetime.timedelta(seconds=int(total)))}"
        )
        MidiPlayerTab.timelineIndicator.configure(text=timelineText)
        bindControls()
        logger.debug(f"switched midi file to: {midiFile}")
    except Exception as e:
        logger.exception(f"switchMidiEvent error: {e}")


# ------------------------
# HOTKEYS (NO-OP ON WAYLAND BUILD)
# ------------------------
def bindControls():
    logger.info("Global hotkeys disabled in this Wayland build (no python key hooks).")


def unbindControls():
    return


# ------------------------
# PLAYBACK UI BUTTONS
# ------------------------
def playButton():
    logger.info("playButton called")
    try:
        # If not running → start
        if not playback_state.running:
            startPlayback()
            return

        # If running → toggle pause
        pausePlayback()
    except Exception as e:
        logger.exception(f"playButton error: {e}")


def startPlayback():
    logger.info("startPlayback called")
    try:
        midiFile = MidiPlayerTab.filePathEntry.get()
        logger.debug(f"startPlayback midiFile: {midiFile}")

        if not midiFile or not os.path.exists(midiFile):
            logger.warning("MIDI File does not exist.")
            threading.Thread(
                target=mainFunctions.insertConsoleText,
                args=("MIDI File does not exist.", True),
                daemon=True
            ).start()
            return

        # mark running
        playback_state.running = True
        playback_state.paused = False

        MidiPlayerTab.playButton.configure(
            text="Playing",
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["PlayingColor"],
            hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["PlayingColorHover"],
        )
        MidiPlayerTab.stopButton.configure(
            state="normal",
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["StopColor"],
        )

        def updateTimeline(text):
            # thread-safe UI update
            MidiPlayerTab.timelineIndicator.after(
                0, lambda: MidiPlayerTab.timelineIndicator.configure(text=text)
            )

        useMIDI = configuration.configData["midiPlayer"]["useMIDIOutput"]

        if useMIDI:
            outputDevice = MidiPlayerTab.outputDeviceDropdown.get()
            logger.debug(f"outputDevice selected: {outputDevice}")
            if not outputDevice:
                threading.Thread(
                    target=mainFunctions.insertConsoleText,
                    args=("No MIDI output device selected.", True),
                    daemon=True
                ).start()
                playback_state.running = False
                return

            useOutput.startPlayback(midiFile, outputDevice, updateCallback=updateTimeline)
            logger.debug("useOutput.startPlayback called")
        else:
            midiHandler.startPlayback(midiFile, updateCallback=updateTimeline)
            logger.debug("midiHandler.startPlayback called")

    except Exception as e:
        playback_state.running = False
        logger.exception(f"startPlayback error: {e}")


def stopPlayback():
    """Stop playback and reset UI state."""
    logger.info("stopPlayback called")

    if not playback_state.running:
        return

    # stop output/macro mode depending on config
    try:
        if configuration.configData["midiPlayer"]["useMIDIOutput"]:
            try:
                useOutput.stopPlayback()
            except Exception:
                pass
        else:
            try:
                midiHandler.stopPlayback()
            except Exception:
                pass
    finally:
        playback_state.running = False
        playback_state.paused = False

    # UI reset
    try:
        MidiPlayerTab.playButton.configure(
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["PlayButtonColor"],
            hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["PlayButtonColorHover"],
            text="Play",
        )
    except Exception:
        pass

    try:
        MidiPlayerTab.stopButton.configure(state="disabled")
    except Exception:
        pass

    try:
        # keep timeline as-is; user might want to replay
        pass
    except Exception:
        pass

    mainFunctions.log("Stopped.")


def pausePlayback():
    """Toggle pause."""
    logger.info("pausePlayback called")

    if not playback_state.running:
        return

    playback_state.paused = not playback_state.paused

    try:
        if configuration.configData["midiPlayer"]["useMIDIOutput"]:
            useOutput.pausePlayback()
        else:
            midiHandler.pausePlayback()
    except Exception:
        pass

    try:
        # show correct label based on playback_state.paused
        MidiPlayerTab.playButton.configure(text="Resume" if playback_state.paused else "Playing")
    except Exception:
        pass

    mainFunctions.log("Paused" if playback_state.paused else "Resumed")


def changeSpeed(amount):
    logger.info("changeSpeed called")
    try:
        if configuration.configData["midiPlayer"]["useMIDIOutput"]:
            useOutput.changeSpeed(amount)
        else:
            midiHandler.changeSpeed(amount)
    except Exception:
        pass
