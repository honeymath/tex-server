export const SERVER_URL = window.location.origin //
export const SOCKET_CHANNEL = "pdf_control";
export const SOCKET_RECEIVE_CHANNEL= "pdf_control_receive";
export const RENDER_SCALE = 1.333;
let filestamp = "" // this storest the latex path to verify if needed to reload the page

// Detect nginx reverse-proxy path prefix from current URL.
// e.g. URL /w/static/static/pdfjs/web/viewer_patched.html → PATH_PREFIX = "/w/static"
// Direct access /static/pdfjs/web/viewer_patched.html → PATH_PREFIX = ""
const prefixMatch = window.location.pathname.match(/^(.*)\/static\/pdfjs\//);
export const PATH_PREFIX = (prefixMatch && prefixMatch[1]) ? prefixMatch[1] : '';

export const socket = io(SERVER_URL, {
  path: PATH_PREFIX ? PATH_PREFIX + '/socket.io/' : '/socket.io/',
  transports: ["websocket"],
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
});

export function setFilestamp(newFilestamp) {
  filestamp = newFilestamp;
}
export function getFilestamp() {
  return filestamp;
}
