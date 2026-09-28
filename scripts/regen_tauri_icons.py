"""根据 logo/LuminOS.png 重新生成桌面端的所有 Tauri 图标。

源图 357x310 略偏矩形（横向有 padding），中心裁成 310x310 正方形作母版，
再 LANZCZOS 缩放到各尺寸；icon.ico 用 Pillow 直接写出多分辨率合集。
"""
from pathlib import Path
from PIL import Image

ROOT = Path(r"d:\桌面\新建文件夹\LuminOS")
SRC = ROOT / "src/frontend/public/logo/LuminOS.png"
ICON_DIR = ROOT / "desktop/src-tauri/icons"

# 1) 取源图基本信息
with Image.open(SRC) as img:
    src_w, src_h = img.size
    # 保留透明通道，源是 RGBA 直接转；如果是 RGB 强制改成 RGBA
    has_alpha = img.mode in ("RGBA", "LA") or (
        img.mode == "P" and "transparency" in img.info
    )
    rgba = img.convert("RGBA") if not has_alpha else img.copy()
print(f"source: {SRC.name}  size={src_w}x{src_h}  mode={img.mode}")

# 2) 中心裁成正方形（取短边为正方形边长）
side = min(src_w, src_h)
left = (src_w - side) // 2
top = (src_h - side) // 2
square = rgba.crop((left, top, left + side, top + side))
print(f"crop to square: {square.size}")

# 母版保存为 icon.png（1024 像素保证所有缩放有足够细节）
master_size = 1024
master = square.resize((master_size, master_size), Image.LANCZOS)
master_path = ICON_DIR / "icon.png"
master.save(master_path, "PNG", optimize=True)
print(f"wrote {master_path.name}  size={master.size}  bytes={master_path.stat().st_size}")

# 3) 落地各尺寸 PNG（不带 alpha 也可以，但保留更灵活）
png_specs = [
    ("32x32.png", 32),
    ("64x64.png", 64),
    ("128x128.png", 128),
    ("128x128@2x.png", 256),  # 实际是 2x，等于 256x256
    # 额外提供 512 / 1024，方便 Windows Store 用 Square*.png 缩放
    ("icon-1024.png", 1024),
]
for name, size in png_specs:
    out = master.resize((size, size), Image.LANCZOS)
    p = ICON_DIR / name
    out.save(p, "PNG", optimize=True)
    print(f"wrote {name}  size={out.size}  bytes={p.stat().st_size}")

# 4) icon.ico：多分辨率合集（Windows 安装包要的）
ico_sizes = [16, 24, 32, 48, 64, 128, 256]
ico_frames = [master.resize((s, s), Image.LANCZOS) for s in ico_sizes]
ico_path = ICON_DIR / "icon.ico"
ico_frames[0].save(
    ico_path,
    format="ICO",
    sizes=[(s, s) for s in ico_sizes],
    append_images=ico_frames[1:],
)
print(f"wrote icon.ico  sizes={ico_sizes}  bytes={ico_path.stat().st_size}")

# 5) icon.icns：macOS 专用，Windows 上一般不重新生成
icns_path = ICON_DIR / "icon.icns"
if icns_path.exists():
    # Pillow 12.1+ 才支持写 icns；不确定当前是否启用，留个标记
    try:
        master.resize((1024, 1024), Image.LANCZOS).save(icns_path, "ICNS")
        print(f"rewrote icon.icns  bytes={icns_path.stat().st_size}")
    except Exception as e:
        print(f"[skip] icon.icns reencode failed ({e}); macOS 用户后续再处理")
else:
    print("[skip] icon.icns not present")

# 6) Square*.png + StoreLogo.png：13 张 Windows Store / MSIX 专用图。
# 一般桌面用户看不到，预留「从母版缩放」的选项，但不默认覆盖；这里只做演示模式。
SQUARE_TARGETS = {
    "Square30x30Logo.png": 30,
    "Square44x44Logo.png": 44,
    "Square71x71Logo.png": 71,
    "Square89x89Logo.png": 89,
    "Square107x107Logo.png": 107,
    "Square142x142Logo.png": 142,
    "Square150x150Logo.png": 150,
    "Square284x284Logo.png": 284,
    "Square310x310Logo.png": 310,
    "StoreLogo.png": 50,
}
write_store = False  # 默认不覆盖，仅打印信息
for name, size in SQUARE_TARGETS.items():
    p = ICON_DIR / name
    if p.exists():
        note = "would overwrite" if write_store else "kept as-is"
        print(f"  {note}: {name} (target {size}px, current {p.stat().st_size}B)")

print("done.")
