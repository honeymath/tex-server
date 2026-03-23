export const SERVER_URL = window.location.origin //
export const SOCKET_CHANNEL = "pdf_control";
export const SOCKET_RECEIVE_CHANNEL= "pdf_control_receive";
export const RENDER_SCALE = 1.333;
let filestamp = "" // this storest the latex path to verify if needed to reload the page
export const socket = io(SERVER_URL, {
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
