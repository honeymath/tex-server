#!/bin/bash

file="$1"
file="${file/#\~/$HOME}"  # 替换 ~ 为 $HOME
line="$2"
col="$3"
filestamp="$4"
pdf="${file%.tex}.pdf"

# 调 synctex view
out=$(synctex view -i "$line:$col:$filestamp" -o "$pdf")
#echo "Command: synctex view -i $line:$col:$filestamp -o $pdf"
#echo "Output from synctex view: $out"
#echo $out > "foo.txt"


# 提取第一个匹配的 page, x, y
page=$(echo "$out" | grep -o 'Page:[^ ]*' | head -n1 | cut -d: -f2)
#echo "Page: $page"
x=$(echo "$out" | grep -o 'x:[^ ]*' | head -n1 | cut -d: -f2)
#echo "X: $x"
y=$(echo "$out" | grep -o 'y:[^ ]*' | head -n1 | cut -d: -f2)
#echo "Y: $y"

refresh=0
for arg in "$@"; do
    if [[ "$arg" == "-r" ]]; then
	    	refresh=1
		echo "Refresh enabled"
	break
    fi
done
### Here is a little foobar to make it smooth
x=100
#echo "Original y: $y"
y=$(echo "$y - 200" | bc)  # 调整 y 位置，避免被工具栏遮挡
#echo "Adjusted y: $y"
# 构造 URL
#see: the original code
#url="http://127.0.0.1:5001/send_pdf_reload?zoom=1.0&filestamp=$(printf %s "$pdf" | jq -sRr @uri)&x=$x&page=$page&y=$y&refresh=$refresh"
#ai: need a new code with loading those config file, 
# 获取配置中的预览地址
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"
url="$LOCAL_PREVIEW_HOST/send_pdf_reload?zoom=1.0&filestamp=$(printf %s "$pdf" | jq -sRr @uri)&x=$x&page=$page&y=$y&refresh=$refresh"
#end
#end
# 调 curl
#echo "Accessing: $url"
curl "$url"

