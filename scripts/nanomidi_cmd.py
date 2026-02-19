#!/usr/bin/env python3
"""Send an IPC command to a running nanoMIDIPlayer instance.

Usage:
  python scripts/nanomidi_cmd.py play
  python scripts/nanomidi_cmd.py pause
  python scripts/nanomidi_cmd.py stop
  python scripts/nanomidi_cmd.py slow_down
  python scripts/nanomidi_cmd.py speed_up
  python scripts/nanomidi_cmd.py tab:0

You typically bind this in Hyprland, e.g.:
  bind = ,F1,exec,python ...
"""

import os
import socket
import sys

def socket_path() -> str:
    base = os.environ.get("XDG_RUNTIME_DIR")

    if not base:
        # fallback if somehow missing (rare on Wayland)
        base = f"/run/user/{os.getuid()}"

    return os.path.join(base, "nanomidiplayer.sock")

def main() -> int:
    if len(sys.argv) < 2:
        print("usage: nanomidi_cmd.py <command>")
        return 2

    cmd = " ".join(sys.argv[1:]).strip()
    path = socket_path()

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.connect(path)
        s.sendall((cmd + "\n").encode("utf-8", "ignore"))
    except FileNotFoundError:
        print(f"IPC socket not found: {path}\nIs nanoMIDIPlayer running?", file=sys.stderr)
        return 1
    except ConnectionRefusedError:
        print(f"IPC connection refused: {path}", file=sys.stderr)
        return 1
    finally:
        try:
            s.close()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
