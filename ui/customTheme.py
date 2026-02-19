import re
import os
import json
import platform
import io
import base64
import sys

import requests
from PIL import Image
import customtkinter as ctk

osName = platform.system()

documentsDir = os.path.join(os.path.expanduser("~"), "Documents")
baseDirectory = os.path.join(documentsDir, "nanoMIDIPlayer")
assetsDirectory = os.path.join(baseDirectory, "assets")
os.makedirs(assetsDirectory, exist_ok=True)

activeThemePath = os.path.join(assetsDirectory, "activeTheme.json")


def resourcePath(relativePath: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        basePath = sys._MEIPASS
    else:
        basePath = os.path.abspath(".")
    return os.path.join(basePath, relativePath)


defaultThemePath = resourcePath("assets/defaultTheme.json")
remoteThemeUrl = "https://raw.githubusercontent.com/NotHammer043/nanoMIDIPlayer/refs/heads/main/api/theme.json"


# -----------------------------
# Safe theme accessor (optional helper)
# -----------------------------
def theme_get(*keys, default="#FFFFFF"):
    data = activeThemeData
    try:
        for key in keys:
            data = data[key]
        return data
    except Exception:
        return default


# -----------------------------
# Deep merge utility
# -----------------------------
def deep_merge(user: dict, default: dict) -> None:
    """
    Fully recursive merge.
    Injects missing nested keys safely.
    """
    for key, default_value in default.items():
        if key not in user:
            user[key] = default_value
            continue

        user_value = user[key]
        if isinstance(user_value, dict) and isinstance(default_value, dict):
            deep_merge(user_value, default_value)
        else:
            # If types differ, prefer default (prevents theme corruption)
            if type(user_value) != type(default_value):
                user[key] = default_value


# -----------------------------
# Theme Loader
# -----------------------------
class SafeDict(dict):
    """
    Dict that never KeyErrors on missing keys.
    BUT: you must DEEP-wrap nested dicts, otherwise nested dicts remain normal dicts.
    """

    def __getitem__(self, key):
        if key not in self:
            return SafeDict()
        value = dict.__getitem__(self, key)
        if isinstance(value, dict) and not isinstance(value, SafeDict):
            value = SafeDict(value)
            self[key] = value
        return value

    def get(self, key, default=None):
        if key not in self:
            return default if default is not None else SafeDict()
        value = dict.get(self, key)
        if isinstance(value, dict) and not isinstance(value, SafeDict):
            value = SafeDict(value)
            self[key] = value
        return value


def deep_safe(obj):
    """
    Recursively convert dicts to SafeDict so nested lookups never KeyError.
    """
    if isinstance(obj, dict) and not isinstance(obj, SafeDict):
        return SafeDict({k: deep_safe(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return [deep_safe(v) for v in obj]
    return obj


class ThemeDict(dict):
    def __init__(self):
        super().__init__()
        self.images = {}
        self.load_theme()

    def fetch_default_theme(self) -> dict:
        try:
            response = requests.get(remoteThemeUrl, timeout=5)
            response.raise_for_status()
            data = response.json()

            selected = configuration.configData.get("theme", data["defaultTheme"])
            themeUrl = data["availableThemes"].get(selected, data["availableThemes"][data["defaultTheme"]])

            themeResponse = requests.get(themeUrl, timeout=5)
            themeResponse.raise_for_status()
            return themeResponse.json()

        except Exception:
            if os.path.exists(defaultThemePath):
                try:
                    with open(defaultThemePath, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass

        return {}

    def _ensure_compat_keys(self, user_dict: dict) -> None:
        """
        Patch missing keys that parts of the UI expect.
        This avoids having to hunt+replace all code locations.
        """
        theme = user_dict.setdefault("Theme", {})
        settings = theme.setdefault("Settings", {})

        # Common expected keys in UI code:
        if "ButtonTextColor" not in settings:
            settings["ButtonTextColor"] = settings.get("TextColor", "#FFFFFF")

        if "ButtonBackColor" not in settings:
            # some files use ButtonBackColor; if missing, fall back to ButtonColor or a neutral
            settings["ButtonBackColor"] = settings.get("ButtonColor", "#2b2b2b")

    def load_theme(self) -> None:
        default = self.fetch_default_theme()

        # Create activeTheme.json if missing
        if not os.path.exists(activeThemePath):
            with open(activeThemePath, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=2)

        # Load user theme file
        try:
            with open(activeThemePath, "r", encoding="utf-8") as f:
                user = json.load(f)
        except Exception:
            user = default

        # Merge defaults into user (fill missing)
        if isinstance(default, dict) and isinstance(user, dict):
            deep_merge(user, default)

        # Inject compatibility keys expected by the UI
        if isinstance(user, dict):
            self._ensure_compat_keys(user)

        # Write back the normalized theme file
        try:
            with open(activeThemePath, "w", encoding="utf-8") as f:
                json.dump(user, f, indent=2)
        except Exception:
            pass

        # IMPORTANT: deep-wrap into SafeDict so nested lookups never KeyError
        safe_user = deep_safe(user if isinstance(user, dict) else {})

        self.clear()
        self.update(safe_user)

        self.load_images()

    def b64_to_img(self, b64: str):
        if b64 in self.images:
            return self.images[b64]
        data = base64.b64decode(b64)
        img = Image.open(io.BytesIO(data))
        self.images[b64] = img
        return img

    def load_images(self) -> None:
        module = sys.modules[__name__]
        
        try:
            icons = self["Theme"]["Icons"]

            def img(name, size):
                return ctk.CTkImage(self.b64_to_img(icons[name]), size=size)

            images = {
                "logoImage": img("banner", (86, 26)),
                "resetImageCTk": img("reset", (16, 16)),
                "pianoImageCTk": img("piano", (20, 20)),
                "drumImageCTk": img("drum", (20, 20)),
                "downloadImageFile": img("download", (18, 18)),
                "searchImageFile": img("search", (18, 18)),
                "settingsImageCTk": img("cogwheel", (18, 18)),
                "keyboardImageCTk": img("keyboard", (18, 18)),
                "infoImageCTk": img("info", (18, 18)),
            }

        except Exception:
            black = Image.new("RGBA", (1, 1))

            def fallback(size):
                return ctk.CTkImage(black, size=size)

            images = {
                "logoImage": fallback((86, 26)),
                "resetImageCTk": fallback((16, 16)),
                "pianoImageCTk": fallback((20, 20)),
                "drumImageCTk": fallback((20, 20)),
                "downloadImageFile": fallback((18, 18)),
                "searchImageFile": fallback((18, 18)),
                "settingsImageCTk": fallback((18, 18)),
                "keyboardImageCTk": fallback((18, 18)),
                "infoImageCTk": fallback((18, 18)),
            }

        # Export to instance + module level
        for name, value in images.items():
            setattr(self, name, value)
            setattr(module, name, value)


# -----------------------------
# GLOBAL THEME
# -----------------------------
activeThemeData = ThemeDict()


# -----------------------------
# Fonts
# -----------------------------
def initializeFonts():
    try:
        fontFamily = activeThemeData["Theme"]["GlobalFont"].get(osName, "Arial")
        if not fontFamily:
            fontFamily = "Arial"
    except Exception:
        fontFamily = "Arial"

    global globalFont11, globalFont12, globalFont14, globalFont20, globalFont40
    globalFont11 = ctk.CTkFont(size=11, weight="bold", family=fontFamily)
    globalFont12 = ctk.CTkFont(size=12, weight="bold", family=fontFamily)
    globalFont14 = ctk.CTkFont(size=14, weight="bold", family=fontFamily)
    globalFont20 = ctk.CTkFont(size=20, weight="bold", family=fontFamily)
    globalFont40 = ctk.CTkFont(size=40, weight="bold", family=fontFamily)


# -----------------------------
# Compatibility wrappers
# -----------------------------
def loadTheme(event=None):
    global activeThemeData
    activeThemeData.load_theme()


def fetchThemes(event=None):
    """Return list[str] of theme names. Works offline using cached theme index."""
    theme_index = _get_theme_index()
    available = theme_index.get("availableThemes") or {}
    return list(available.keys())


# ---------------------------
# Theme index + offline cache
# ---------------------------

def _theme_cache_dir() -> str:
    # Cache under ~/.config/nanoMIDIPlayer/themes (per-user, persistent, no sudo)
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    d = os.path.join(base, "nanoMIDIPlayer", "themes")
    os.makedirs(d, exist_ok=True)
    return d


def _theme_index_cache_path() -> str:
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    d = os.path.join(base, "nanoMIDIPlayer")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "theme_index.json")


def _safe_load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _safe_save_json(path: str, data) -> None:
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        pass


def _slugify(name: str) -> str:
    s = "".join(ch.lower() if ch.isalnum() else "_" for ch in (name or "theme"))
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "theme"


def _get_theme_index() -> dict:
    """Return theme.json contents. Prefer online, fallback to cached index, then local api/theme.json."""
    # 1) online
    try:
        r = requests.get(remoteThemeUrl, timeout=5)
        if r.status_code == 200:
            data = r.json()
            _safe_save_json(_theme_index_cache_path(), data)
            return data
    except Exception:
        pass

    # 2) cached index
    cached = _safe_load_json(_theme_index_cache_path())
    if isinstance(cached, dict) and cached.get("availableThemes"):
        return cached

    # 3) local api/theme.json (ships with repo)
    local = _safe_load_json(resourcePath("api/theme.json"))
    if isinstance(local, dict) and local.get("availableThemes"):
        return local

    return {"defaultTheme": "Dark", "availableThemes": {"Dark": ""}}


def _get_theme_url_map() -> dict:
    return (_get_theme_index().get("availableThemes") or {})


def _theme_cache_path_for(name: str) -> str:
    return os.path.join(_theme_cache_dir(), f"{_slugify(name)}.json")


def _download_theme_to_cache(name: str, url: str) -> str | None:
    if not url:
        return None
    try:
        r = requests.get(url, timeout=7)
        if r.status_code != 200:
            return None
        data = r.json()
        path = _theme_cache_path_for(name)
        _safe_save_json(path, data)
        return path
    except Exception:
        return None


def switchTheme(themeName=None):
    """
    Called by the Settings theme combobox (command=customTheme.switchTheme).
    - Tries to download the selected theme JSON
    - Falls back to cached theme JSON when offline
    - Falls back to local api/themes/*.json as last resort
    """
    # CTkComboBox passes the selected value as first arg
    if themeName is None:
        return

    try:
        configuration.configData["theme"] = themeName
    except Exception:
        pass

    url_map = _get_theme_url_map()
    url = url_map.get(themeName, "")

    # 1) online download -> cache
    theme_path = None
    if url:
        theme_path = _download_theme_to_cache(themeName, url)

    # 2) cached theme file
    if theme_path is None:
        p = _theme_cache_path_for(themeName)
        if os.path.exists(p):
            theme_path = p

    # 3) local api/themes fallback
    if theme_path is None:
        slug = _slugify(themeName)
        candidates = [
            resourcePath(os.path.join("api", "themes", f"{slug}.json")),
            resourcePath(os.path.join("api", "themes", f"{slug.replace('_', '')}.json")),
        ]
        for lp in candidates:
            if os.path.exists(lp):
                theme_path = lp
                break
        if theme_path is None:
            lp = resourcePath(os.path.join("api", "themes", "dark.json"))
            if os.path.exists(lp):
                theme_path = lp

    if theme_path:
        activeThemeData.load_theme(theme_path)
        return

    try:
        logger.warning(f"Theme '{themeName}' could not be loaded (offline and no cache).")
    except Exception:
        pass
