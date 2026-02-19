import base64
import json
import io
from PIL import Image
import os

with open("activeTheme.json", "r", encoding="utf-8") as f:
    theme = json.load(f)

icons = theme["Theme"]["Icons"]

output_dir = "theme_icons"
os.makedirs(output_dir, exist_ok=True)

for name, data in icons.items():

    if not isinstance(data, str) or data.startswith("IF YOU"):
        continue

    try:
        img = Image.open(io.BytesIO(base64.b64decode(data)))
        path = os.path.join(output_dir, f"{name}.png")
        img.save(path)
        print("Saved:", path)

    except Exception:
        print("Skipped:", name)
