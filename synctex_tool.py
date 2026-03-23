#!/usr/bin/env python3
"""
SyncTeX 工具 - 纯计算的 CLI 工具
从 syncpdf.py 和 pdfsync_decode.py 提取，零外部依赖

用法:
  synctex_tool.py forward --synctex <path> --searchfile <path> --line <N> --json-dir <dir>
  synctex_tool.py reverse --page <N> --x <F> --y <F> --json-dir <dir>
"""

import os
import sys
import json
import gzip
import argparse


def parse_synctex(synctex_path):
    """
    解析 synctex 文件，返回 records 和 file_map
    来源: syncpdf.py:13-68
    """
    data = []
    files = {}
    with open(synctex_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    content_mode = False
    current_pdf_page_index = None

    for line in lines:
        line = line.strip()
        # 解析 Input 行获取文件映射
        if line.startswith("Input:"):
            _, file_index, file_path = line.split(":")
            files[file_index] = os.path.normpath(file_path)

        if not content_mode:
            if line.startswith("Content:"):
                content_mode = True
        else:
            if line.startswith("{") and line[1:].isdigit():
                current_pdf_page_index = int(line[1:]) - 1
            elif line.startswith("}") and line[1:].isdigit():
                current_pdf_page_index = None
            elif line.startswith("!"):
                continue
            elif current_pdf_page_index is not None and line and (line[0].isalpha() or line[0] in "($)"):
                record_type = ''
                i = 0
                while i < len(line) and not line[i].isdigit() and line[i] not in "([":
                    record_type += line[i]
                    i += 1
                try:
                    left, coords_part = line[len(record_type):].split(":", 1)
                    file_num_str, line_num_str = left.split(",", 1)
                    file_num = int(file_num_str)
                    line_num = int(line_num_str)
                    pdf_coords = coords_part.split(":")[0]
                    pdf_x, pdf_y = map(float, pdf_coords.split(","))
                    data.append({
                        "type": record_type,
                        "tag": file_num,
                        "line": line_num,
                        "file_num": file_num,
                        "pdf_page_index": current_pdf_page_index,
                        "pdf_x": pdf_x / 65536.0,
                        "pdf_y": pdf_y / 65536.0
                    })
                except:
                    pass
    return data, files


def build_forward_map(records):
    """
    构建正向映射: {file_num -> {line -> {x, y, page}}}
    来源: syncpdf.py:82-98
    """
    forward_map = {}
    seen = set()
    for rec in records:
        key = (rec['file_num'], rec['line'])
        if key not in seen:
            seen.add(key)
            forward_map.setdefault(str(rec['file_num']), {})[str(rec['line'])] = {
                "x": rec['pdf_x'],
                "y": rec['pdf_y'],
                "page": rec['pdf_page_index'] + 1
            }
    # 排序 key
    forward_map_sorted = {k: dict(sorted(v.items(), key=lambda kv: int(kv[0])))
                          for k, v in sorted(forward_map.items(), key=lambda kv: int(kv[0]))}
    return forward_map_sorted


def build_reverse_map(records):
    """
    构建反向映射: {page -> {y -> {x -> [file_num, line]}}}
    来源: syncpdf.py:100-128
    """
    reverse_map = {}
    for rec in records:
        page = str(rec['pdf_page_index'] + 1)  # 1-based page
        y = f"{rec['pdf_y']:.2f}"
        x = f"{rec['pdf_x']:.2f}"
        reverse_map.setdefault(page, {}).setdefault(y, {})
        reverse_map[page][y][x] = [rec['file_num'], rec['line']]

    # 合并相邻 x，并排序
    for page, ydict in reverse_map.items():
        new_ydict = {}
        for y, xdict in sorted(ydict.items(), key=lambda kv: float(kv[0])):
            xs_sorted = sorted(xdict.keys(), key=lambda v: float(v))
            merged = {}
            prev_x = None
            prev_val = None
            for x in xs_sorted:
                val = xdict[x]
                if prev_x is not None and val == prev_val:
                    continue
                merged[x] = val
                prev_x = x
                prev_val = val
            new_ydict[y] = merged
        reverse_map[page] = new_ydict

    reverse_map_sorted = dict(sorted(reverse_map.items(), key=lambda kv: int(kv[0])))
    return reverse_map_sorted


def forward_lookup(forward_map, file_map, searchfile, line):
    """
    正向查找: 给定源文件和行号，返回 PDF 坐标
    来源: syncpdf.py:207-254 (handler 函数中的逻辑)

    返回: {"page": int, "x": float, "y": float}
    """
    # 规范化搜索文件路径
    path = os.path.normpath(os.path.expanduser(searchfile)).strip()
    filekey = None

    # 在 file_map 中查找文件索引
    for key, value in file_map.items():
        if value.strip() == path:
            filekey = key
            break

    if filekey is None:
        raise Exception(f"Error: not able to find file {path}")

    if filekey not in forward_map:
        raise Exception(f"Not able to identify the file in the forward map {path} with filekey {filekey}")

    line_dict = forward_map[filekey]
    parsed_lines = sorted(map(int, line_dict.keys()))

    # 找到 <= line 的最大行号
    until = None
    for l in parsed_lines:
        if l <= line:
            until = l
        else:
            break

    if until is None:
        # 如果没有找到，使用第一行（通常发生在序言部分）
        until = parsed_lines[0]

    result = line_dict[str(until)]
    return {
        "page": result["page"],
        "x": result["x"],
        "y": result["y"]
    }


def reverse_lookup(reverse_map, file_map, page, x, y):
    """
    反向查找: 给定 PDF 坐标，返回源文件和行号
    来源: pdfsync_decode.py:9-65 (handler 函数)

    返回: {"file": str, "line": int}
    """
    page = str(page)

    if page not in reverse_map:
        raise Exception(f"Cannot identify page {page} in the reverse map")

    page_details = reverse_map[page]
    all_y = sorted(map(float, page_details.keys()))

    # 找到 > y 的最小 y 坐标
    nexty = None
    for val in all_y:
        if val > y:
            nexty = val
            break
    if nexty is None:
        raise Exception(f"No y-coordinate greater than {y} found for page {page}")

    line_details = page_details[f"{nexty:.2f}"]
    all_x = sorted(map(float, line_details.keys()))

    # 找到 > x 的最小 x 坐标
    nextx = None
    for val in all_x:
        if val > x:
            nextx = val
            break
    if nextx is None:
        nextx = all_x[-1]

    fileindex, line = line_details[f"{nextx:.2f}"]
    fileindex = str(fileindex)

    if fileindex not in file_map:
        raise Exception(f"Not able to find the file index {fileindex} in the file map")

    filepath = os.path.normpath(os.path.expanduser(file_map[fileindex])).strip()

    return {
        "file": filepath,
        "line": line
    }


def cmd_forward(args):
    """处理 forward 子命令"""
    synctex_path = args.synctex

    # 如果是 .gz 文件，先解压
    if synctex_path.endswith('.gz'):
        uncompressed_path = synctex_path[:-3]  # 去掉 .gz 后缀
        try:
            with gzip.open(synctex_path, 'rb') as f_in:
                with open(uncompressed_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            synctex_path = uncompressed_path
        except Exception as e:
            print(f"Error during gunzip: {e}", file=sys.stderr)
            sys.exit(1)

    # 解析 synctex 文件
    records, file_map = parse_synctex(synctex_path)

    # 构建映射
    forward_map = build_forward_map(records)
    reverse_map = build_reverse_map(records)

    # 保存 JSON 文件到指定目录
    json_dir = args.json_dir
    os.makedirs(json_dir, exist_ok=True)

    with open(os.path.join(json_dir, "forward_map.json"), "w", encoding="utf-8") as f:
        json.dump(forward_map, f, indent=2)

    with open(os.path.join(json_dir, "reverse_map.json"), "w", encoding="utf-8") as f:
        json.dump(reverse_map, f, indent=2)

    with open(os.path.join(json_dir, "file_map.json"), "w", encoding="utf-8") as f:
        json.dump(file_map, f, indent=2)

    # 正向查找
    result = forward_lookup(forward_map, file_map, args.searchfile, args.line)

    # 输出 JSON 结果
    print(json.dumps(result))


def cmd_reverse(args):
    """处理 reverse 子命令"""
    json_dir = args.json_dir

    # 读取已保存的映射文件
    with open(os.path.join(json_dir, "reverse_map.json"), "r", encoding="utf-8") as f:
        reverse_map = json.load(f)

    with open(os.path.join(json_dir, "file_map.json"), "r", encoding="utf-8") as f:
        file_map = json.load(f)

    # 反向查找
    result = reverse_lookup(reverse_map, file_map, args.page, args.x, args.y)

    # 输出 JSON 结果
    print(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(
        description='SyncTeX 工具 - 正向/反向搜索',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # forward 子命令
    parser_forward = subparsers.add_parser('forward', help='正向搜索: 源文件+行号 -> PDF 坐标')
    parser_forward.add_argument('--synctex', required=True, help='synctex 文件路径 (.synctex 或 .synctex.gz)')
    parser_forward.add_argument('--searchfile', required=True, help='源文件绝对路径')
    parser_forward.add_argument('--line', type=int, required=True, help='行号')
    parser_forward.add_argument('--json-dir', required=True, help='JSON 映射文件保存目录')

    # reverse 子命令
    parser_reverse = subparsers.add_parser('reverse', help='反向搜索: PDF 坐标 -> 源文件+行号')
    parser_reverse.add_argument('--page', type=int, required=True, help='PDF 页码 (1-based)')
    parser_reverse.add_argument('--x', type=float, required=True, help='PDF x 坐标')
    parser_reverse.add_argument('--y', type=float, required=True, help='PDF y 坐标')
    parser_reverse.add_argument('--json-dir', required=True, help='JSON 映射文件读取目录')

    args = parser.parse_args()

    if args.command == 'forward':
        cmd_forward(args)
    elif args.command == 'reverse':
        cmd_reverse(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
