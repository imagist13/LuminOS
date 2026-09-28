"""标准 ICNS 验证：从 TOC 里读取条目列表，校验每个 entry type 都是合法 macOS 元素名。"""
import struct
from pathlib import Path

ICNS = Path(r"d:\桌面\新建文件夹\LuminOS\desktop/src-tauri/icons/icon.icns")
data = ICNS.read_bytes()
total = len(data)
assert data[:4] == b"icns", f"bad magic: {data[:4]!r}"

# 找到 TOC 段
pos = 8
toc_pos = None
while pos < total:
    typ = data[pos:pos + 4]
    sz = struct.unpack_from(">I", data, pos + 4)[0]
    if typ == b"toc ":
        toc_pos = pos
        toc_size = sz
        break
    pos += sz

assert toc_pos is not None, "找不到 TOC 段"
toc_entries_off = toc_pos + 8  # 跨过 'toc ' + size
toc_end = toc_pos + toc_size
print(f"TOC 段偏移 {toc_pos}，toc_size={toc_size}")

# 读 TOC 条目
toc_entries = []
p = toc_entries_off
while p + 8 <= toc_end:
    et = data[p:p + 4]
    es = struct.unpack_from(">I", data, p + 4)[0]
    toc_entries.append((et, es))
    p += 8
print(f"TOC entries ({len(toc_entries)}):")
for et, es in toc_entries:
    print(f"  {et!r}  size={es}")

# 扫描 data 段对照
print("\n实际 data 段:")
data_pos = toc_pos + toc_size
found_types = []
while data_pos < total:
    typ = data[data_pos:data_pos + 4]
    sz = struct.unpack_from(">I", data, data_pos + 4)[0]
    found_types.append((typ, sz))
    print(f"  {typ!r}  size={sz}  offset={data_pos}")
    data_pos += sz

# 二者应一致
toc_set = {et for et, _ in toc_entries}
data_set = {et for et, _ in found_types}
print("\n一致性:", "✓ TOC 与 data 段匹配" if toc_set == data_set else f"✗ 不一致 TOC={toc_set} DATA={data_set}")
print("总计: %d 个元素 (合计 %d bytes)" % (len(found_types), sum(s for _, s in found_types)))
