"""手写一个标准 ICNS 编码器，纠正 Pillow 输出的非标 ICNS。

ICNS 文件结构：
  'icns' (4 bytes, ASCII)
  file_size (uint32 big-endian, 含前 8 字节)
  toc_section:
    'toc ' (4 bytes) + toc_size (4 bytes BE) +
      [每 8 字节：entry_type (4 ASCII) + entry_size (4 BE, 含 type+size+data)]
  data_sections:
    [entry_type (4) + entry_size (4 BE) + PNG bytes]

标准元素类型：
  icp4 16, icp5 32, icp6 64, ic07 128, ic08 256, ic09 512, ic10 1024
"""
import io
import struct
from pathlib import Path
from PIL import Image

ICON_DIR = Path(r"d:\桌面\新建文件夹\LuminOS\desktop/src-tauri/icons")
MASTER = ICON_DIR / "icon.png"

# 标准 macOS 元素类型与对应像素尺寸
ICNS_ENTRIES = [
    ("icp4", 16),
    ("icp5", 32),
    ("icp6", 64),
    ("ic07", 128),
    ("ic08", 256),
    ("ic09", 512),
    ("ic10", 1024),
]

with Image.open(MASTER) as m:
    master = m.convert("RGBA")

# 为每个尺寸准备 PNG 字节
elements = []
for code, size in ICNS_ENTRIES:
    img = master.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    elements.append((code, buf.getvalue()))

# 拼装 TOC（占位：先计算大小）
def build_icns(elements):
    # 先算 data 部分每段：type(4) + size(4 BE) + PNG bytes
    data_blocks = []
    for code, png in elements:
        block_size = 8 + len(png)
        data_blocks.append(block_size)
    # TOC 段大小：8 + 每条目 8 字节
    toc_size = 8 + len(elements) * 8
    # 文件总大小：8（魔数+file_size） + toc_size + sum(data_blocks)
    file_size = 8 + toc_size + sum(data_blocks)

    out = io.BytesIO()
    # magic + file size
    out.write(b"icns")
    out.write(struct.pack(">I", file_size))
    # TOC section
    out.write(b"toc ")
    out.write(struct.pack(">I", toc_size))
    for (code, png), block_size in zip(elements, data_blocks):
        out.write(code.encode("ascii"))
        out.write(struct.pack(">I", block_size))
    # Data sections
    for (code, png), block_size in zip(elements, data_blocks):
        out.write(code.encode("ascii"))
        out.write(struct.pack(">I", block_size))
        out.write(png)
    return out.getvalue()

icns_bytes = build_icns(elements)
ICNS = ICON_DIR / "icon.icns"
ICNS.write_bytes(icns_bytes)
print(f"wrote icon.icns  {ICNS.stat().st_size} bytes")

# 校验：解析回来看看元素表
pos = 8
elements_found = []
total = len(icns_bytes)
while pos < total:
    t = icns_bytes[pos:pos + 4]
    s = struct.unpack_from(">I", icns_bytes, pos + 4)[0]
    elements_found.append((t, s))
    pos += 8 + (s - 8) if s > 8 else 0  # 防呆，防 size 包含 header
    break  # 只看 TOC 一次
print(f"TOC: {elements_found}")
# 进入 data 段
print(f"\n解析所有数据段:")
pos = 8 + struct.unpack_from(">I", icns_bytes, 8)[0]  # skip TOC
while pos < total:
    t = icns_bytes[pos:pos + 4]
    s = struct.unpack_from(">I", icns_bytes, pos + 4)[0]
    print(f"  {t!r}  size={s}  next_offset={pos + s}")
    pos += s
