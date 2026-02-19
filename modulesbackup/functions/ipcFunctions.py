"""nanoMIDIPlayer IPC for Wayland/Hyprland global hotkeys.

Problem this solves
------------------
On Linux, the popular `keyboard` Python library hooks into /dev/input.
That *usually* requires root, and on Wayland it is often unreliable.

Hyprland (and other compositors) can do global keybinds reliably.
This module provides a tiny UNIX-socket server inside the app so
those keybinds can send commands to nanoMIDIPlayer.

Commands (one per line)
----------------------
  play | pause | stop | slow_down | speed_up
  tab:0 ... tab:4

The handler is implemented in modules.functions.mainFunctions.dispatchIpcCommand.
"""

from __future__ import annotations

import os
import socket
import threading
import logging

from pathlib import Path

from modules.functions import mainFunctions

logger = logging.getLogger("modules.functions.ipcFunctions")


_server_thread: threading.Thread | None = None
_stop_event = threading.Event()
_sock_path: str | None = None


def get_default_socket_path() -> str:
    # Prefer XDG runtime dir (best for sockets). Fallback to ~/.cache.
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    if runtime:
        p = Path(runtime) / "nanomidiplayer.sock"
        return str(p)
    p = Path.home() / ".cache" / "nanoMIDIPlayer" / "nanomidiplayer.sock"
    return str(p)


def start(socket_path: str | None = None) -> str:
    """Start the IPC server (idempotent). Returns the socket path."""
    global _server_thread, _sock_path

    if _server_thread and _server_thread.is_alive():
        return _sock_path or get_default_socket_path()

    _stop_event.clear()
    _sock_path = socket_path or get_default_socket_path()

    # Ensure directory exists
    try:
        Path(_sock_path).parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    _server_thread = threading.Thread(
        target=_run_server,
        name="nanoMIDIPlayer-IPC",
        daemon=True,
    )
    _server_thread.start()
    logger.info("IPC server started at %s", _sock_path)
    return _sock_path


# Backwards-compatible alias: some code paths call start_ipc_server(app=self)
# even though this IPC server does not need the app instance.
def start_ipc_server(app=None, socket_path: str | None = None) -> str:  # noqa: ARG001
    """Alias for start() used by older/forked main.py."""
    return start(socket_path=socket_path)


def stop() -> None:
    """Stop the IPC server."""
    global _sock_path
    _stop_event.set()

    # Nudge accept() by connecting once
    if _sock_path and os.path.exists(_sock_path):
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect(_sock_path)
                s.sendall(b"\n")
        except Exception:
            pass


def _run_server() -> None:
    assert _sock_path is not None

    # Remove stale socket
    try:
        if os.path.exists(_sock_path):
            os.remove(_sock_path)
    except Exception:
        pass

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as srv:
        srv.bind(_sock_path)
        srv.listen(5)
        srv.settimeout(0.5)

        # Make socket user-only by default
        try:
            os.chmod(_sock_path, 0o600)
        except Exception:
            pass

        while not _stop_event.is_set():
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                continue
            except Exception as e:
                logger.debug("IPC accept error: %s", e)
                continue

            with conn:
                try:
                    data = conn.recv(4096)
                except Exception:
                    continue

                if not data:
                    continue

                # Can contain multiple lines
                try:
                    text = data.decode("utf-8", errors="ignore")
                except Exception:
                    continue

                for line in text.splitlines():
                    cmd = line.strip()
                    if not cmd:
                        continue
                    _dispatch_to_tk(cmd)

    # Cleanup
    try:
        if _sock_path and os.path.exists(_sock_path):
            os.remove(_sock_path)
    except Exception:
        pass


def _dispatch_to_tk(cmd: str) -> None:
    app = mainFunctions.getApp()
    if not app:
        return

    # Ensure Tk-thread execution
    try:
        app.after(0, lambda: mainFunctions.dispatchIpcCommand(cmd))
    except Exception as e:
        logger.debug("IPC dispatch failed: %s", e)
