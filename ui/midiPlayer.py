import customtkinter as ctk
import tkinter as tk

from modules import configuration
import ui.customTheme as customTheme
from ui.widget.tooltip import ToolTip

class MidiPlayerTab(ctk.CTkFrame):
    def __init__(self, master):
        from modules.functions import midiPlayerFunctions
        from modules.functions import mainFunctions
        from modules.functions import settingsFunctions
        super().__init__(master)
        customTheme.initializeFonts()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.midiFrame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["BackgroundColor"]
        )

        self.midiFrame.grid(row=0, column=0, sticky="nsew")
        self.midiFrame.grid_rowconfigure(4, weight=1)
        self.midiFrame.grid_columnconfigure(0, weight=1)
        self.midiFrame.grid_columnconfigure(1, weight=1)

        self.topBar = ctk.CTkFrame(
            self.midiFrame,
            fg_color="transparent"
        )
        self.topBar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20,10))

        self.topBar.grid_columnconfigure(0, weight=1)
        self.topBar.grid_columnconfigure(1, weight=1)

        self.outputDeviceLabel = ctk.CTkLabel(
            self.midiFrame, text="MIDI Output Device", fg_color="transparent", font=customTheme.globalFont14, 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.outputDeviceLabel.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")

        self.midiToggleSwitch = ctk.CTkSwitch(
            self.midiFrame, text="Use MIDI Output", command=midiPlayerFunctions.switchUseMIDI, variable=midiPlayerFunctions.switchUseMIDIvar, font=customTheme.globalFont14, 
            onvalue="on", offvalue="off", fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchDisabled"], 
            progress_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchEnabled"], 
            button_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchCircle"], 
            button_hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchCircleHovered"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.midiToggleSwitch.grid(row=0, column=1, padx=20, pady=(10, 0), sticky="e")
        ToolTip.CreateToolTip(self.midiToggleSwitch, text = 'Simulates MIDI signals to the\nselected MIDI Output Device\n\nNOTE: Having this enabled won\'t simulate\nQWERTY Keys for you if you\'re looking to macro.')

        self.outputDeviceDropdown = ctk.CTkOptionMenu(
            self.midiFrame, values=["Loading..."], font=customTheme.globalFont14, 
            dropdown_font=customTheme.globalFont14, command=None, 
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["OptionBackColor"], 
            dropdown_fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["OptionDropdownBackground"], 
            button_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["OptionDropdownButtonColor"], 
            button_hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["OptionDropdownButtonHoverColor"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.outputDeviceDropdown.grid(row=1, column=0, padx=20, sticky="ew")
        self.__class__.outputDeviceDropdown = self.outputDeviceDropdown
        self.__class__.midiToggleSwitch = self.midiToggleSwitch
        ToolTip.CreateToolTip(self.outputDeviceDropdown, text = 'Selected MIDI Output Device')

        self.refreshOutputDevices = ctk.CTkButton(
            self.midiFrame, image=customTheme.resetImageCTk, text="", width=30, command=mainFunctions.refreshOutputDevices, 
            font=customTheme.globalFont14, 
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["ButtonColor"], 
            hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["ButtonHoverColor"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.refreshOutputDevices.grid(row=1, column=1, padx=5, sticky="e")
        ToolTip.CreateToolTip(self.refreshOutputDevices, text = 'Refresh MIDI Output Devices List')

        # MIDI FILE SELECTION
        self.filePathLabel = ctk.CTkLabel(
            self.midiFrame, text="MIDI File Path", fg_color="transparent", font=customTheme.globalFont14, 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.filePathLabel.grid(row=2, column=0, sticky="w", padx=20)

        self.filePathEntry = ctk.CTkOptionMenu(
            self.midiFrame, width=350, values="", command=midiPlayerFunctions.switchMidiEvent, font=customTheme.globalFont14, 
            dropdown_font=customTheme.globalFont14, 
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["OptionBackColor"], 
            dropdown_fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["OptionDropdownBackground"], 
            button_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["OptionDropdownButtonColor"], 
            button_hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["OptionDropdownButtonHoverColor"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.filePathEntry.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.__class__.filePathEntry = self.filePathEntry
        ToolTip.CreateToolTip(self.filePathEntry, text = 'Selected MIDI File')

        self.selectFileButton = ctk.CTkButton(
            self.midiFrame, text="Select File", command=midiPlayerFunctions.selectFile, font=customTheme.globalFont14, 
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["ButtonColor"], 
            hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["ButtonHoverColor"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.selectFileButton.grid(row=2, column=1, sticky="e", padx=20)
        ToolTip.CreateToolTip(self.selectFileButton, text = 'Select MIDI File (.mid | .midi)')

        # CONSOLE
        self.consoleFrame = tk.Frame(
            master=self.midiFrame,
            height=180,
            bg=customTheme.activeThemeData["Theme"]["MidiPlayer"]["ConsoleBackground"]
        )
        self.consoleFrame.grid_propagate(False)
        self.consoleFrame.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        self.__class__.consoleFrame = self.consoleFrame

        # HOTKEYS FRAME
        self.hotkeysFrame = ctk.CTkFrame(self.midiFrame, fg_color="transparent")
        self.hotkeysFrame.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        for i in range(6):
            self.hotkeysFrame.grid_columnconfigure(i, weight=1)

        # HOTKEYS
        self.playHotkeyLabel = ctk.CTkLabel(
            self.hotkeysFrame, text=" Play:", fg_color="transparent", font=customTheme.globalFont14, 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )

        self.playHotkeyLabel.grid(row=0, column=0, sticky="w")

        self.playHotkeyButton = ctk.CTkButton(
            self.hotkeysFrame, text=configuration.configData["hotkeys"].get('play', 'f1').upper(), width=70, command=mainFunctions.playHotkeyCommand, 
            font=customTheme.globalFont14, 
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["HotkeySelectorColor"], 
            hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["HotkeySelectorHoverColor"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.playHotkeyButton.grid(row=1, column=0, sticky="w")
        self.__class__.playHotkeyButton = self.playHotkeyButton
        ToolTip.CreateToolTip(self.playHotkeyButton, text = 'Start Playback Hotkey')

        self.pauseHotkeyLabel = ctk.CTkLabel(
            self.hotkeysFrame, text="Pause:", fg_color="transparent", font=customTheme.globalFont14, 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )

        self.pauseHotkeyLabel.grid(row=0, column=1, sticky="w")

        self.pauseHotkeyButton = ctk.CTkButton(
            self.hotkeysFrame, text=configuration.configData["hotkeys"].get('pause', 'f2').upper(), width=70, command=mainFunctions.pauseHotkeyCommand, 
            font=customTheme.globalFont14, 
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["HotkeySelectorColor"], 
            hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["HotkeySelectorHoverColor"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.pauseHotkeyButton.grid(row=1, column=1, sticky="w")
        self.__class__.pauseHotkeyButton = self.pauseHotkeyButton
        ToolTip.CreateToolTip(self.pauseHotkeyButton, text = 'Pause Playback Hotkey')

        self.stopHotkeyLabel = ctk.CTkLabel(
            self.hotkeysFrame, text=" Stop:", fg_color="transparent", font=customTheme.globalFont14, 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )

        self.stopHotkeyLabel.grid(row=0, column=2, sticky="w")

        self.stopHotkeyButton = ctk.CTkButton(
            self.hotkeysFrame, text=configuration.configData["hotkeys"].get('stop', 'f3').upper(), width=70, command=mainFunctions.stopHotkeyCommand, 
            font=customTheme.globalFont14, 
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["HotkeySelectorColor"], 
            hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["HotkeySelectorHoverColor"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.stopHotkeyButton.grid(row=1, column=2, sticky="w")
        self.__class__.stopHotkeyButton = self.stopHotkeyButton
        ToolTip.CreateToolTip(self.stopHotkeyButton, text = 'Stop Playback Hotkey')

        self.slowDownHotkeyLabel = ctk.CTkLabel(
            self.hotkeysFrame, text="Slow Down:", fg_color="transparent", font=customTheme.globalFont14, 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )

        self.slowDownHotkeyLabel.grid(row=0, column=4, sticky="w")

        self.speedUpHotkeyButton = ctk.CTkButton(
            self.hotkeysFrame, text=configuration.configData["hotkeys"].get('speedup', 'f4').upper(), width=70, command=mainFunctions.speedUpHotkeyCommand, 
            font=customTheme.globalFont14, 
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["HotkeySelectorColor"], 
            hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["HotkeySelectorHoverColor"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.speedUpHotkeyButton.grid(row=1, column=3, sticky="w")
        self.__class__.speedUpHotkeyButton = self.speedUpHotkeyButton
        ToolTip.CreateToolTip(self.speedUpHotkeyButton, text = 'Speed-up Playback Hotkey')

        self.speedUpHotkeyLabel = ctk.CTkLabel(
            self.hotkeysFrame, text=" Speed Up:", fg_color="transparent", font=customTheme.globalFont14, 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )

        self.speedUpHotkeyLabel.grid(row=0, column=3, sticky="w")

        self.slowHotkeyButton = ctk.CTkButton(
            self.hotkeysFrame, text=configuration.configData["hotkeys"].get('slowdown', 'f5').upper(), width=70, command=mainFunctions.slowHotkeyCommand, 
            font=customTheme.globalFont14, 
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["HotkeySelectorColor"], 
            hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["HotkeySelectorHoverColor"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.slowHotkeyButton.grid(row=1, column=4, sticky="w")
        self.__class__.slowHotkeyButton = self.slowHotkeyButton
        ToolTip.CreateToolTip(self.slowHotkeyButton, text = 'Slow-down Playback Hotkey')
        
        # TOGGLES
        self.sustainToggle = ctk.CTkSwitch(
            self.hotkeysFrame, text="Sustain   ", command=midiPlayerFunctions.switchSustain, variable=midiPlayerFunctions.switchSustainvar, font=customTheme.globalFont14, 
            onvalue="on", offvalue="off", fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchDisabled"], 
            progress_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchEnabled"], 
            button_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchCircle"], 
            button_hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchCircleHovered"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.sustainToggle.grid(row=2, column=0, pady=(10, 0), sticky="w")
        self.__class__.sustainToggle = self.sustainToggle
        ToolTip.CreateToolTip(self.sustainToggle, text = 'Simulates Pedal by "Spacebar"\nOnly works on supported games.')

        self.noDoublesToggle = ctk.CTkSwitch(
            self.hotkeysFrame, text="No Doubles", command=midiPlayerFunctions.switchNoDoubles, variable=midiPlayerFunctions.switchNoDoublesvar, font=customTheme.globalFont14, 
            onvalue="on", offvalue="off", fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchDisabled"], 
            progress_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchEnabled"], 
            button_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchCircle"], 
            button_hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchCircleHovered"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.noDoublesToggle.grid(row=3, column=0, pady=(5, 0), sticky="w")
        self.__class__.noDoublesToggle = self.noDoublesToggle
        ToolTip.CreateToolTip(self.noDoublesToggle, text = 'Prevents double-triggering of keys')

        self.velocityToggle = ctk.CTkSwitch(
            self.hotkeysFrame, text="Velocity  ", command=midiPlayerFunctions.switchVelocity, variable=midiPlayerFunctions.switchVelocityvar, font=customTheme.globalFont14, 
            onvalue="on", offvalue="off", fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchDisabled"], 
            progress_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchEnabled"], 
            button_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchCircle"], 
            button_hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchCircleHovered"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.velocityToggle.grid(row=4, column=0, pady=(5, 0), sticky="w")
        self.__class__.velocityToggle = self.velocityToggle
        ToolTip.CreateToolTip(self.velocityToggle, text = 'Simulates how hard a key is pressed by "CTRL"\nwhich affects the loudness of that note\nOnly works on supported games.')

        self.use88KeysToggle = ctk.CTkSwitch(
            self.hotkeysFrame, text="88 Keys   ", command=midiPlayerFunctions.switch88Keys, variable=midiPlayerFunctions.switch88Keysvar, font=customTheme.globalFont14, 
            onvalue="on", offvalue="off", fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchDisabled"], 
            progress_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchEnabled"], 
            button_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchCircle"], 
            button_hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SwitchCircleHovered"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.use88KeysToggle.grid(row=5, column=0, pady=(5, 10), sticky="w")
        self.__class__.use88KeysToggle = self.use88KeysToggle
        ToolTip.CreateToolTip(self.use88KeysToggle, text = 'Simulate LowNote and HighNote by "CTRL"\nOnly works on supported games.')

        # PLAYBACK BUTTONS
        self.playButton = ctk.CTkButton(
            self.hotkeysFrame, text="Play", fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["PlayColor"], 
            width=80, command=midiPlayerFunctions.playButton, font=customTheme.globalFont14, 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"], 
            hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["PlayColorHover"]
        )
        self.playButton.grid(row=8, column=0, sticky="w")
        self.__class__.playButton = self.playButton
        ToolTip.CreateToolTip(self.playButton, text = 'Start Playback')

        self.stopButton = ctk.CTkButton(
            self.hotkeysFrame, text="Stop", fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["StopColorDisabled"], 
            width=80, state="disabled", command=midiPlayerFunctions.stopPlayback, font=customTheme.globalFont14, 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"], 
            hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["StopColorHover"]
        )
        self.stopButton.grid(row=8, column=1, sticky="w")
        self.__class__.stopButton = self.stopButton

        # TIMER
        self.timelineText = "0:00:00 / 0:00:00" if configuration.configData['appUI']['timestamp'] else "X:XX:XX / 0:00:00"

        self.timelineIndicator = ctk.CTkLabel(
            self.hotkeysFrame, text=self.timelineText, fg_color="transparent", font=customTheme.globalFont14, 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.timelineIndicator.grid(row=8, column=5, sticky="e")
        self.__class__.timelineIndicator = self.timelineIndicator

        # SPEED CONTROL
        self.speedTextTitle = ctk.CTkLabel(
            self.hotkeysFrame, text="Speed", fg_color="transparent", font=customTheme.globalFont14, 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.speedTextTitle.grid(row=6, column=0, columnspan=6, pady=(10, 0))

        self.speedSlider = ctk.CTkSlider(
            self.hotkeysFrame, from_=1, to=500, command=lambda value: settingsFunctions.updateFromSlider("midiSpeedController", value), 
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SpeedSliderBackColor"], width=190,
            progress_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SpeedSliderFillColor"], 
            button_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SpeedSliderCircleColor"], 
            button_hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SpeedSliderCircleHoverColor"]
        )
        self.speedSlider.grid(row=7, column=1, columnspan=3, sticky="ew", pady=(5, 0))
        self.__class__.speedSlider = self.speedSlider
        self.speedSlider.set(100)
        ToolTip.CreateToolTip(self.speedSlider, text = 'Playback Speed')

        self.resetSpeedButton = ctk.CTkButton(
            self.hotkeysFrame, image=customTheme.resetImageCTk, text="", width=30, command=lambda: settingsFunctions.resetControl("midiSpeedController"), 
            font=customTheme.globalFont14, 
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["ButtonColor"], 
            hover_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["ButtonHoverColor"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"], 
            text_color_disabled=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColorDisabled"]
        )
        self.resetSpeedButton.grid(row=7, column=5, padx=5, pady=(5, 0))
        ToolTip.CreateToolTip(self.resetSpeedButton, text = 'Reset Speed')

        self.speedValueEntry = ctk.CTkEntry(
            self.hotkeysFrame, placeholder_text="100", width=50, 
            fg_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SpeedValueBoxBackColor"], 
            font=customTheme.globalFont14, 
            border_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["SpeedValueBoxBorderColor"], 
            text_color=customTheme.activeThemeData["Theme"]["MidiPlayer"]["TextColor"]
        )
        self.speedValueEntry.grid(row=7, column=4, padx=5, pady=(5, 0))
        self.__class__.speedValueEntry = self.speedValueEntry
        self.speedValueEntry.insert(0, "100")
        ToolTip.CreateToolTip(self.speedValueEntry, text = 'Speed Value')

        self.speedValueEntry.bind("<FocusOut>", lambda value: settingsFunctions.updateFromEntry("midiSpeedControllcer", value))
        self.speedValueEntry.bind("<KeyRelease>", lambda value: settingsFunctions.updateFromEntry("midiSpeedController", value))
        self.speedSlider.bind("<ButtonRelease-1>", lambda value: settingsFunctions.updateFromEntry("midiSpeedController", value))

        self.midiFrame.grid_rowconfigure(99, weight=1)

        mainFunctions.insertConsoleText("Hello! :)", ignoreConsoleCheck=False)