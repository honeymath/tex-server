import { RENDER_SCALE, SERVER_URL, SOCKET_CHANNEL, setFilestamp, getFilestamp, socket, PATH_PREFIX } from "./config.js";
import { EDITOR_BRIDGE_ENABLED, EDITOR_BRIDGE_URL } from "./user_config.js";

let timestamp = 0;
let fresh = true;

function refreshPage() {
    fresh = true;
    console.log("🔄 Refreshing the page...");
    window.location.reload();
}

function updatePageLocation(data) {
    let filestamp = getFilestamp();
    console.log("Function has been called with data: " + JSON.stringify(data));

    const viewer = window.PDFViewerApplication;
    const page = data.page;
    let zoom = data.zoom || 1.0;
    const x = data.x || 0;
    const y = data.y || 0;
    const refresh = data.refresh || 0;

    console.log("Updating page location with data: " + JSON.stringify({ page, zoom, x, y, timestamp: data.timestamp, filestamp: data.filestamp, refresh }));

    try {
        if (timestamp != 0 && data.timestamp == timestamp) {
            console.log("Timestamp is the same, no action taken.");
            return;
        }
        timestamp = data.timestamp;
        filestamp = data.filestamp;
        setFilestamp(filestamp);
        console.log("Fresh variable is currently: " + fresh);
        if (!fresh) {
            console.log("Fresh variable is false, I am going to check the refresh..");
            if (refresh > 0) {
                refreshPage();
                return;
            }
        }
        fresh = false;
    } catch (error) {
        alert("Error in timestamp or filestamp check: " + error);
    }

    try {
        viewer.pdfViewer.currentPageNumber = parseInt(page, 10);
//        viewer.pdfViewer.currentScaleValue = zoom;
//	    viewer.pdfViewer._setScale(zoom, true);
	    	console.log(`Setting page number to ${page} and scale to ${zoom}`);
        console.log('Finished setting up page number and scale of pdfViewer');
    } catch (error) {
        alert(error);
    }

    setTimeout(() => {
        const pageElement = document.querySelector(`.page[data-page-number='${page}']`);
        let zoom = window.PDFViewerApplication.pdfViewer.currentScale;
	console.log("getting the current zoom: " + zoom);
        if (pageElement) {
            const scrollX = x * zoom * RENDER_SCALE;
            const scrollY = y * zoom * RENDER_SCALE;
            viewer.pdfViewer.container.scrollTo({
                top: pageElement.offsetTop + scrollY - 200, //give user an expericne of tking middle
                left: scrollX,
                behavior: "smooth"
            });
            console.log(`🔍 Scrolled to page ${page}, X=${scrollX}, Y=${scrollY}`);
//see: Please see the foolowing code, and let me know why this red line created does not behave well when I zoom in and out
            // 插入红线标记
/*
            const marker = document.createElement('div');
            marker.style.position = 'absolute';
            marker.style.left = '0';
            marker.style.width = '100%';
            marker.style.height = '3px';
            marker.style.background = 'red';
            marker.style.top = `${scrollY+200*zoom*RENDER_SCALE}px`;
            marker.style.pointerEvents = 'none';

            pageElement.style.position = 'relative';
            pageElement.appendChild(marker);

            console.log(`🖌️ Added marker at Y=${scrollY} on page ${page}`);
*/

//end
//ai: please create a blue line here
// 插入蓝线标记（随页面缩放）
const blueMarker = document.createElement('div');
blueMarker.style.position = 'absolute';
blueMarker.style.left = '0';
blueMarker.style.width = '100%';
blueMarker.style.height = '3px';
blueMarker.style.opacity = '0.6';
blueMarker.style.borderRadius = '2px';
blueMarker.style.transition = 'opacity 0.3s ease-in-out';
blueMarker.style.zIndex = '1000';
blueMarker.style.background = 'red';
blueMarker.style.top = `${scrollY}px`;
blueMarker.style.pointerEvents = 'none';

const canvasWrapper = pageElement.querySelector('.canvasWrapper') || pageElement;
canvasWrapper.style.position = 'relative';
canvasWrapper.appendChild(blueMarker);

function updateBlueMarkerPosition() {
    const zoom = viewer.pdfViewer.currentScale;
    const scrollY = y * zoom * RENDER_SCALE;
    const markerY = scrollY// + 200 * zoom * RENDER_SCALE;
    blueMarker.style.top = `${markerY}px`;
    console.log(`🔵 Repositioned blue marker at Y=${markerY}`);
}
viewer.eventBus.on("scalechanging", updateBlueMarkerPosition);

console.log(`🔵 Added blue marker at Y=${scrollY} on page ${page}`);
//end
            // 自动移除 marker（例如 3 秒后）
 //           setTimeout(() => marker.remove(), 3000);
        } else {
            console.warn("⚠️ Page element not found.");
        }
    }, 1200);
}


function handleReload() {
    if (document.visibilityState === "visible") {
        console.log("👁️ Document is now visible");
        fetch(PATH_PREFIX + '/send_pdf_reload')
            .then(response => response.json())
            .then(data => {
                console.log("📄 Reload data received:", data);
                updatePageLocation(data);
            });
    }
}

socket.on("connect", () => {
    console.log("🔌 Connected to the server");
    handleReload();
});

socket.on("disconnect", () => {
    console.log("🔌 Disconnected from the server");
});

socket.on(SOCKET_CHANNEL, (data) => {
    console.log("📥 Received control message:", data);
    if (data.type === "reload" && window.PDFViewerApplication) {
        updatePageLocation(data);
    }
});

socket.on("reverse_search_result", (data) => {
    console.log("reverse_search_result received:", data);
    if (!EDITOR_BRIDGE_ENABLED || data.error) return;
    const url = `${EDITOR_BRIDGE_URL}/open?filename=${encodeURIComponent(data.file)}&line=${data.line}`;
    console.log("Opening editor:", url);
    fetch(url, { mode: "no-cors" }).catch((err) => {
        console.warn("Editor bridge request failed:", err);
    });
});

document.addEventListener("visibilitychange", handleReload);
window.addEventListener("load", handleReload);
document.getElementById('toolbarContainer').style.display = 'none';
document.getElementById('sidebarContainer').style.display = 'none';
//see:Paste your code over here
// ⌨️ 添加按键监听器，按下 'd' 键自动下载 PDF 文件

document.addEventListener('keydown', function (event) {
    if (event.key === 'd' && !event.ctrlKey && !event.metaKey) {
        const link = document.createElement('a');
        link.href = window.PDFViewerApplication.url;
        link.download = window.PDFViewerApplication.url.split('/').pop();
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        console.log('⬇️ 按下 "d" 触发文件下载！');
    }
});
//end
