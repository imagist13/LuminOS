"""用 struct 直接解析 ICO/ICNS 文件头验证实际帧数和分辨率。"""
import struct
from pathlib import Path

ICO = Path(r"d:\桌面\新建文件夹\LuminOS\desktop/src-tauri/icons/icon.ico")
data = ICO.read_bytes()
# ICONDIR: reserved(2) + type(2) + count(2)
reserved, kind, count = struct.unpack_from("<HHH", data, 0)
print(f"icon.ico  reserved={reserved}  type={kind}  count={count}")
# ICONDIRENTRY: 16 bytes per entry: width(1) + height(1) + palette(1) + reserved(1)
# + planes(2) + bitcount(2) + size(4) + offset(4)
entries = []
for i in range(count):
    off = 6 + i * 16
    w_b, h_b, _pal, _res, planes, bpp, size, _offset = struct.unpack_from("<BBBBHHII", data, off)
    w = 256 if w_b == 0 else w_b
    h = 256 if h_b == 0 else h_b
    entries.append((w, h, planes, bpp, size))
print("frames:")
for w, h, planes, bpp, size in entries:
    print(f"  {w}x{h}  planes={planes} bpp={bpp}  bytes={size}")

# ICNS: magic 'icns'(4) + size(4) + <element: type(4) + size(4) + data>
ICNS = Path(r"d:\桌面\新建文件夹\LuminOS\desktop/src-tauri/icons/icon.icns")
icns = ICNS.read_bytes()
magic, total = struct.unpack_from(">4sI", icns, 0)
print(f"\nicon.icns  magic={magic.decode()}  total={total} bytes")
# 遍历元素
pos = 8
elements = []
while pos < total:
    et_raw, es = struct.unpack_from(">4sI", icns, pos)
    elements.append((et_raw, es))
    pos += 8 + es
print(f"elements: {len(elements)}")
for et, es in elements:
    print(f"  {et!r}  size={es}")
