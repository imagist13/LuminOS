"""补写 icon.ico（多分辨率合集）和 icon.icns（Pillow 12 用 sizes 参数）。"""
from pathlib import Path
from PIL import Image

ICON_DIR = Path(r"d:\桌面\新建文件夹\LuminOS\desktop\src-tauri\icons")
MASTER = ICON_DIR / "icon.png"  # 1024x1024 RGBA 母版

with Image.open(MASTER) as m:
    master = m.convert("RGBA")
print(f"master: {master.size} {master.mode}")

# ICO: Pillow 自动从单一源图缩放出 sizes 列表中的每一帧，PNG 编码嵌入（Vista+ 标准）
ico_sizes = [(s, s) for s in (16, 24, 32, 48, 64, 128, 256)]
ico_path = ICON_DIR / "icon.ico"
master.save(ico_path, format="ICO", sizes=ico_sizes)
print(f"wrote icon.ico  sizes={ico_sizes}  bytes={ico_path.stat().st_size}")

# ICNS: 标准 macOS 图标尺寸（icp4 ~ 16, icp5 ~ 32, icp6 ~ 64, ic07 ~ 128, ic08 ~ 256, ic09 ~ 512, ic10 ~ 1024）
icns_sizes = [16, 32, 64, 128, 256, 512, 1024]
icns_path = ICON_DIR / "icon.icns"
master.save(icns_path, format="ICNS", sizes=icns_sizes)
print(f"wrote icon.icns  sizes={icns_sizes}  bytes={icns_path.stat().st_size}")

# 验证
for f in (ico_path, icns_path):
    with Image.open(f) as img:
        frames = []
        n = 0
        try:
            while True:
                img.seek(n)
                frames.append(img.size)
                n += 1
        except EOFError:
            pass
        print(f"{f.name}: frames={n}, sizes={frames}")
