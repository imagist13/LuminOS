"""验证 icon.ico 实际包含哪些分辨率（858B 太小，可能缺帧）。"""
from PIL import Image
from pathlib import Path

ICO = Path(r"d:\桌面\新建文件夹\LuminOS\desktop\src-tauri\icons\icon.ico")
print(f"file size: {ICO.stat().st_size} bytes")

with Image.open(ICO) as ico:
    sizes = []
    n = 0
    while True:
        try:
            ico.seek(n)
            sizes.append(ico.size)
            n += 1
        except EOFError:
            break
print(f"frames: {n}")
print(f"sizes:  {sizes}")

# 也读 icon.icns 校验
ICNS = Path(r"d:\桌面\新建文件夹\LuminOS\desktop\src-tauri\icons\icon.icns")
print(f"\nicns size: {ICNS.stat().st_size} bytes")
if ICNS.exists():
    with Image.open(ICNS) as icns:
        sizes = []
        n = 0
        while True:
            try:
                icns.seek(n)
                sizes.append(icns.size)
                n += 1
            except EOFError:
                break
        print(f"icns frames: {n}, sizes: {sizes}")
