import { RENDER_SCALE,SERVER_URL, SOCKET_RECEIVE_CHANNEL, setFilestamp,getFilestamp, socket } from "./config.js";
// 📄 double_click_page_position.js
// 监听 PDF 页面上的双击事件，获取页号和页内坐标 ✨（支持 zoom 缩放）

console.log("The socket receive channel is:", SOCKET_RECEIVE_CHANNEL);

function sendMessage(socket, data) {
  if (socket && socket.connected) {
    socket.emit(SOCKET_RECEIVE_CHANNEL, data);
    console.log("消息已发送到 Socket.IO 服务器:", data);
  } else {
    console.error("Socket.IO 未连接或已关闭");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const viewerContainer = document.getElementById("viewerContainer");

  if (viewerContainer) {
    viewerContainer.addEventListener("dblclick", (event) => {
      // 找到点击位置对应的 PDF 页
      let targetElement = event.target;
      while (targetElement && !targetElement.classList.contains("page")) {
        targetElement = targetElement.parentElement;
      }

      if (targetElement) {
        const pageNumber = targetElement.getAttribute("data-page-number");

        // 计算在 page 内部的 DOM 坐标
        const rect = targetElement.getBoundingClientRect();
        const pageX_dom = event.clientX - rect.left;
        const pageY_dom = event.clientY - rect.top;

        // 获取当前缩放比例
        let currentScale = 1;
        try {
          currentScale = PDFViewerApplication.pdfViewer.currentScale || 1;
        } catch (e) {
          console.warn("无法获取 currentScale，默认使用 1，错误信息：", e);
        }

        // 还原成 PDF 页内原始坐标（未缩放）
        const pageX_pdf = pageX_dom / (currentScale* RENDER_SCALE);
        const pageY_pdf = pageY_dom / (currentScale * RENDER_SCALE);

        //alert(`你双击了第 ${pageNumber} 页\n在该页中的位置（页面坐标）：X=${pageX_dom.toFixed(1)}, Y=${pageY_dom.toFixed(1)}\n原始 PDF 坐标：X=${pageX_pdf.toFixed(1)}, Y=${pageY_pdf.toFixed(1)}`);
        // 发送消息到 WebSocket 服务器
	sendMessage(socket, {
	  pageNumber: parseInt(pageNumber, 10),
	  pageX_pdf: parseFloat(pageX_pdf.toFixed(1)),
	  pageY_pdf: parseFloat(pageY_pdf.toFixed(1)),
	  filestamp: getFilestamp(),
	});

        console.log(`Page ${pageNumber} | DOM X=${pageX_dom}, Y=${pageY_dom} | PDF X=${pageX_pdf}, Y=${pageY_pdf}`);
      } else {
        alert(`你双击了非 PDF 区域`);
      }
    });
  } else {
    console.warn("没有找到 viewerContainer 元素喵～ 🐾");
  }
});
