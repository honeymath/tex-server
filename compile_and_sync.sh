#!/bin/bash
#
# compile_and_sync.sh - LaTeX 编译 + PDF 正向搜索脚本
#
# 用法: compile_and_sync.sh <searchfile> <line> [zoom] [refresh] [output_dir]
#
#   searchfile   - 当前编辑的 .tex 文件的路径
#   line         - 光标所在行号
#   zoom         - 缩放比例 (默认 1.0)
#   refresh      - 是否刷新 (默认 1)
#   output_dir   - PDF/synctex 输出目录 (默认 $SCRIPT_DIR/static)
#
# 服务器地址和端口从 config.ini 读取。
# PDF 输出到 <脚本所在目录>/static/main.pdf。
#
# 如果向上找不到 main.tex，则直接编译指定的文件，
# 产出仍命名为 main.pdf / main.synctex.gz。
#
# 示例:
#   ./compile_and_sync.sh /path/to/chapter.tex 42
#

set -euo pipefail

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# === 从 config.ini 读取服务器端口 ===
CONFIG_FILE="$SCRIPT_DIR/config.ini"
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "错误: config.ini 不存在: $CONFIG_FILE" >&2
    echo "请从 config.ini.example 拷贝并配置。" >&2
    exit 1
fi

# === 检查参数 ===
if [[ $# -lt 2 ]]; then
    echo "用法: $0 <searchfile> <line> [zoom] [refresh] [output_dir]" >&2
    echo "" >&2
    echo "参数说明:" >&2
    echo "  searchfile   - 当前编辑的 .tex 文件路径" >&2
    echo "  line         - 光标行号" >&2
    echo "  zoom         - 缩放比例 (默认 1.0)" >&2
    echo "  refresh      - 是否刷新 (默认 1)" >&2
    echo "  output_dir   - 输出目录 (默认 \$SCRIPT_DIR/static)" >&2
    exit 1
fi

SEARCHFILE="$1"
LINE="$2"
ZOOM="${3:-1.0}"
REFRESH="${4:-1}"
OUTPUT_DIR="${5:-$SCRIPT_DIR/static}"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" 2>/dev/null && pwd || echo "$OUTPUT_DIR")"
DIR_NAME="$(basename "$OUTPUT_DIR")"

# === 从 config.ini 解析端口: [workspaces] > [server] ===
PORT=$(python3 -c "
import configparser, sys
c = configparser.ConfigParser()
c.read('$CONFIG_FILE')
dir_name = '$DIR_NAME'
if c.has_section('workspaces') and c.has_option('workspaces', dir_name):
    print(c.get('workspaces', dir_name))
else:
    print(c.get('server', 'port'))
")
PREVIEW_HOST="http://127.0.0.1:${PORT}"

# 验证参数
if [[ ! -f "$SEARCHFILE" ]]; then
    echo "错误: 文件不存在: $SEARCHFILE" >&2
    exit 1
fi

# 转为绝对路径（synctex 中记录的是绝对路径）
SEARCHFILE="$(cd "$(dirname "$SEARCHFILE")" && pwd)/$(basename "$SEARCHFILE")"

if ! [[ "$LINE" =~ ^[0-9]+$ ]]; then
    echo "错误: 行号必须是数字: $LINE" >&2
    exit 1
fi

# === 查找 main.tex（向上查找） ===
find_main_tex() {
    local current_file="$1"
    local current_dir

    if [[ -f "$current_file" ]]; then
        current_dir="$(dirname "$current_file")"
    else
        current_dir="$current_file"
    fi

    current_dir="$(cd "$current_dir" && pwd)"

    while true; do
        if [[ -f "$current_dir/main.tex" ]]; then
            echo "$current_dir/main.tex"
            return 0
        fi

        if [[ "$current_dir" == "/" ]]; then
            return 1
        fi

        current_dir="$(dirname "$current_dir")"
    done
}

# === 确定编译目标 ===
echo "==> 查找 main.tex..."
if MAIN_TEX="$(find_main_tex "$SEARCHFILE")"; then
    echo "找到: $MAIN_TEX"
    COMPILE_DIR="$(dirname "$MAIN_TEX")"
    COMPILE_TARGET="main.tex"
    BASENAME="main"
else
    echo "未找到 main.tex，直接编译: $SEARCHFILE"
    SEARCHFILE_ABS="$(cd "$(dirname "$SEARCHFILE")" && pwd)/$(basename "$SEARCHFILE")"
    COMPILE_DIR="$(dirname "$SEARCHFILE_ABS")"
    COMPILE_TARGET="$(basename "$SEARCHFILE_ABS")"
    BASENAME="${COMPILE_TARGET%.tex}"
fi

cd "$COMPILE_DIR"

# === 清理旧的产物，避免编译失败时残留过期数据 ===
echo "==> 清理旧的 synctex 和 map 文件..."
rm -f "$OUTPUT_DIR/main.synctex.gz" "$OUTPUT_DIR/main.synctex"
rm -f "$OUTPUT_DIR/forward_map.json" "$OUTPUT_DIR/reverse_map.json" "$OUTPUT_DIR/file_map.json"

echo ""
echo "==> 编译 LaTeX 文档..."
echo "工作目录: $COMPILE_DIR"
echo "编译目标: $COMPILE_TARGET"
echo ""

# 编译
pdflatex -synctex=1 -interaction=nonstopmode "$COMPILE_TARGET"

COMPILE_EXIT_CODE=$?
if [[ $COMPILE_EXIT_CODE -ne 0 ]]; then
    echo ""
    echo "编译失败 (退出码: $COMPILE_EXIT_CODE)" >&2
    exit $COMPILE_EXIT_CODE
fi

# === 拷贝 PDF 到 static 目录 ===
echo ""
echo "==> 拷贝 PDF 到 $OUTPUT_DIR ..."

PDF_FILE="$COMPILE_DIR/${BASENAME}.pdf"
if [[ ! -f "$PDF_FILE" ]]; then
    echo "错误: PDF 未生成: $PDF_FILE" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
cp "$PDF_FILE" "$OUTPUT_DIR/main.pdf"
echo "PDF 已拷贝到: $OUTPUT_DIR/main.pdf"

# === 拷贝 synctex 到 static 目录 ===
SYNCTEX_FILE="$COMPILE_DIR/${BASENAME}.synctex.gz"
if [[ ! -f "$SYNCTEX_FILE" ]]; then
    echo "错误: 未找到 synctex 文件: $SYNCTEX_FILE" >&2
    exit 1
fi

cp "$SYNCTEX_FILE" "$OUTPUT_DIR/main.synctex.gz"
echo "synctex 已拷贝到: $OUTPUT_DIR/main.synctex.gz"

# === 正向搜索 ===
echo ""
echo "==> 解析 synctex 并进行正向搜索..."

COORDS_JSON=$(python3 "$SCRIPT_DIR/synctex_tool.py" forward \
    --synctex "$OUTPUT_DIR/main.synctex.gz" \
    --searchfile "$SEARCHFILE" \
    --line "$LINE" \
    --json-dir "$OUTPUT_DIR")

echo "查找结果: $COORDS_JSON"

PAGE=$(echo "$COORDS_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['page'])")
X=$(echo "$COORDS_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['x'])")
Y=$(echo "$COORDS_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['y'])")

echo ""
echo "==> 通知 PDF viewer..."
echo "原始坐标: 第 $PAGE 页, x=$X, y=$Y"

X_ADJUSTED=100
Y_ADJUSTED=$Y
echo "调整后坐标: x=$X_ADJUSTED, y=$Y_ADJUSTED"

CURL_URL="${PREVIEW_HOST}/send_pdf_reload"
CURL_PARAMS="page=${PAGE}&x=${X_ADJUSTED}&y=${Y_ADJUSTED}&zoom=${ZOOM}&refresh=${REFRESH}"

if curl -s -f "${CURL_URL}?${CURL_PARAMS}" > /dev/null 2>&1; then
    echo "PDF viewer 已更新"
else
    echo "警告: 无法连接到 PDF viewer (${PREVIEW_HOST})" >&2
    echo "请检查 pdf_server.py 是否运行" >&2
fi

echo ""
echo "完成!"
