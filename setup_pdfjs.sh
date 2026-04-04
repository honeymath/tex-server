#!/bin/bash
# 用法: ./setup_pdfjs.sh <pdfjs-version>
# 例如: ./setup_pdfjs.sh 5.3.31
#
# 下载 PDF.js 到 ../pdf.js，然后 patch viewer.html。
# 之后自动创建 symlink: static/pdfjs -> ../../pdf.js

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: $0 <pdfjs-version> (e.g. 5.3.31)"
    exit 1
fi

URL="https://github.com/mozilla/pdf.js/releases/download/v${VERSION}/pdfjs-${VERSION}-legacy-dist.zip"
ZIPFILE="pdfjs-${VERSION}-legacy-dist.zip"
TARGET_DIR="$SCRIPT_DIR/../pdf.js"

echo "Downloading PDF.js v${VERSION} from ${URL}..."
curl -L -o "${ZIPFILE}" "${URL}"

rm -rf "${TARGET_DIR}"
echo "Unzipping to ${TARGET_DIR} ..."
python3 -m zipfile -e "${ZIPFILE}" "${TARGET_DIR}"

echo "Running generate_injected_pdfjs_viewer.py..."
python3 "$SCRIPT_DIR/generate_injected_pdfjs_viewer.py"

echo "Cleaning up zip..."
rm "${ZIPFILE}"

# Create symlink if not exists
if [ ! -e "$SCRIPT_DIR/static/pdfjs" ]; then
    ln -s ../../pdf.js "$SCRIPT_DIR/static/pdfjs"
    echo "Created symlink: static/pdfjs -> ../../pdf.js"
fi

echo "Done! PDF.js v${VERSION} ready in ${TARGET_DIR}."
