import customtkinter as ctk
import threading
import platform
import os

import ui.customTheme as customTheme
from modules.functions import midiHubFunctions
from modules.functions import mainFunctions

osName = platform.system()

class MidiHubTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        customTheme.initializeFonts()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.mainScrollFrame = ctk.CTkScrollableFrame(
            self, corner_radius=0, 
            fg_color=customTheme.activeThemeData["Theme"]["MIDIHub"]["BackgroundColor"]
        )
        self.mainScrollFrame.grid(row=0, column=0, sticky="nsew")
        self.mainScrollFrame.grid_columnconfigure(0, weight=0)
        self.mainScrollFrame.grid_columnconfigure(1, weight=1)
        self.mainScrollFrame.grid_rowconfigure(0, weight=1)
        self.__class__.mainScrollFrame = self.mainScrollFrame

                # --- scrolling fix ---
        def _is_descendant(widget, ancestor):
            try:
                while widget is not None:
                    if widget == ancestor:
                        return True
                    widget = widget.master
            except Exception:
                return False
            return False

        def _on_wheel(event):
            if not _is_descendant(event.widget, self.mainScrollFrame):
                return

            canvas = getattr(self.mainScrollFrame, "_parent_canvas", None)
            if canvas is None:
                return

            if getattr(event, "delta", 0):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                return

            num = getattr(event, "num", None)
            if num == 4:
                canvas.yview_scroll(-3, "units")
            elif num == 5:
                canvas.yview_scroll(3, "units")

        self.midiDataApiUrl = "https://api.nanomidi.net/api/midiData"
        self.pageSize = 10
        self.currentPage = 1
        
        def handleSearch(event=None):
            threading.Thread(target=None, args=(event,)).start()

        self.searchEntry = ctk.CTkEntry(
            self.mainScrollFrame, 
            placeholder_text="Search", 
            width=240, 
            font=customTheme.globalFont14, 
            fg_color=customTheme.activeThemeData["Theme"]["MIDIHub"]["SearchBarColor"], 
            text_color=customTheme.activeThemeData["Theme"]["MIDIHub"]["TextColor"], 
            border_color=customTheme.activeThemeData["Theme"]["MIDIHub"]["SearchBarBorderColor"]
        )
        self.searchEntry.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")
        self.searchEntry.bind("<Return>", handleSearch)
        self.__class__.searchEntry = self.searchEntry

        self.searchButton = ctk.CTkButton(
            master=self.mainScrollFrame, 
            text="", 
            fg_color=customTheme.activeThemeData["Theme"]["MIDIHub"]["SearchButtonColor"], 
            hover_color=customTheme.activeThemeData["Theme"]["MIDIHub"]["SearchButtonHoverColor"], 
            width=24, 
            height=24, 
            command=midiHubFunctions.filteredMidiData, 
            image=customTheme.searchImageFile
        )
        self.searchButton.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="e")
        self.__class__.searchButton = self.searchButton
            
        self.sortComboBox = ctk.CTkComboBox(
            master=self.mainScrollFrame, 
            values=["Newest", "Oldest", "Downloads", "Views"], 
            text_color=customTheme.activeThemeData["Theme"]["MIDIHub"]["TextColor"], 
            button_color=customTheme.activeThemeData["Theme"]["MIDIHub"]["SortOptionDropdownButtonColor"], 
            fg_color=customTheme.activeThemeData["Theme"]["MIDIHub"]["SortOptionBackColor"], 
            dropdown_fg_color=customTheme.activeThemeData["Theme"]["MIDIHub"]["SortOptionDropdownBackground"], 
            dropdown_font=customTheme.globalFont14,
            command=midiHubFunctions.sortComboCommand, 
            width=105, 
            font=customTheme.globalFont14, 
            button_hover_color=customTheme.activeThemeData["Theme"]["MIDIHub"]["SortOptionDropdownButtonHoverColor"], 
            dropdown_hover_color=customTheme.activeThemeData["Theme"]["MIDIHub"]["SortOptionDropdownItemHover"], 
            border_color=customTheme.activeThemeData["Theme"]["MIDIHub"]["SortOptionBorderColor"]
        )
        self.sortComboBox.grid(row=0, column=0, padx=56, pady=(10, 0), sticky="e")
        self.sortComboBox.configure(state="readonly")
        self.__class__.sortComboBox = self.sortComboBox
