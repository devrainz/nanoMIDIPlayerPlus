import ui.customTheme as customTheme
from modules import configuration
from tkinter import Toplevel, LEFT, SOLID, Label


class ToolTip:
    def __init__(self, widget, text=None):
        customTheme.initializeFonts()

        self.widget = widget
        self.text = text
        self.tipwindow = None

        if text:
            self.bind_events()

    # -----------------------------

    def bind_events(self):
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    # -----------------------------

    def enter(self, _event=None):
        if not configuration.configData["appUI"]["tooltip"]:
            return

        if self.tipwindow or not self.text:
            return

        x = self.widget.winfo_rootx() + 40
        y = self.widget.winfo_rooty() + 25

        self.tipwindow = tw = Toplevel(self.widget)

        # CRITICAL for Hyprland:
        tw.wm_overrideredirect(True)
        tw.attributes("-type", "tooltip")  # prevents compositor focus stealing
        tw.attributes("-topmost", True)

        tw.geometry(f"+{x}+{y}")

        Label(
            tw,
            text=self.text,
            justify=LEFT,
            fg="#ffffff",
            background="#151515",
            relief=SOLID,
            borderwidth=1,
            font=customTheme.globalFont14,
        ).pack(ipadx=4, ipady=2)

    # -----------------------------

    def leave(self, _event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

    # Backwards compatibility
    @staticmethod
    def CreateToolTip(widget, text):
        ToolTip(widget, text)
