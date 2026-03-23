#!/bin/bash
# 用法: ./update_pdfjs.sh 5.3.31
# 目标: 解压到 ../pdf.js

set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: $0 <pdfjs-version> (e.g. 5.3.31)"
    exit 1
fi

URL="https://github.com/mozilla/pdf.js/releases/download/v${VERSION}/pdfjs-${VERSION}-legacy-dist.zip"
ZIPFILE="pdfjs-${VERSION}-legacy-dist.zip"
TARGET_DIR="../pdf.js"

echo "Downloading PDF.js v${VERSION} from ${URL}..."
curl -L -o "${ZIPFILE}" "${URL}"

rm -rf "${TARGET_DIR}"  # 防止旧的还在
echo "Unzipping to ../pdf.js ..."
#unzip -o "${ZIPFILE}" -d ../pdf.js
python3 -m zipfile -e "${ZIPFILE}" ../pdf.js


echo "Running inject_socket.py..."
python3 generate_injected_pdfjs_viewer.py

echo "Cleaning up zip..."
rm "${ZIPFILE}"

echo "Done! PDF.js v${VERSION} ready in ${TARGET_DIR}."

