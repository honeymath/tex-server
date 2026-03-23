
from flask import Blueprint, request, jsonify
from socketapp import socketio, state
import traceback
import time


pdf_routes = Blueprint('pdf_routes', __name__)

@pdf_routes.route("/send_pdf_reload", methods=["GET", "POST"])
def send_pdf_reload():
    try:
        # Read parameters
        if request.method == "POST":
            data = request.get_json()
            print(f"[DEBUG] Received POST /send_pdf_reload data: {data}")
        elif request.method == "GET":
            data = request.args.to_dict()
            print(f"[DEBUG] Received GET /send_pdf_reload params: {data}")

        # Extract parameters with type checking
        try:
            if "page" not in data:
                return jsonify(state.get("data", {})), 200
            ## Explaination: If "page" is not given, this scrupt runs as another function of looking up the state that last time was set.
            page = int(data.get("page"))
            zoom = float(data.get("zoom"))
            x = float(data.get("x"))
            y = float(data.get("y"))
            state["data"] = data ## askGPT if this needs to globalize state or not
        except (TypeError, ValueError) as parse_err:
            print(f"[ERROR] Parameter parsing error: {parse_err}")
            return jsonify({
                "error": "Invalid parameter types. Expecting: page=int, zoom=float, x=float, y=float.",
                "exception": str(parse_err)
            }), 400

        # Build message
        message = {
            "type": "reload",
            "page": page,
            "zoom": zoom,
            "x": x,
            "y": y,
            "timestamp": time.time(),
            "filestamp": data.get("filestamp", None),  # Optional, can be None
            "refresh": data.get("refresh", 0)  # Optional, default to False
        }

        # Emit message to WebSocket
        try:
            socketio.emit("pdf_control", message)
 #           broadcast_queue.put(message)
            print(f"[INFO] Sent pdf_control message successfully: {message}")
        except Exception as emit_err:
            print(f"[ERROR] Failed to emit pdf_control message: {emit_err}")
            return jsonify({
                "error": "Failed to emit WebSocket message.",
                "exception": str(emit_err),
                "message": message
            }), 500

        # Return success response
        return jsonify({
            "status": "ok",
            "message": message
        })

    except Exception as e:
        print(f"[FATAL ERROR] Unexpected error in /send_pdf_reload: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "Unexpected server error.",
            "exception": str(e),
            "traceback": traceback.format_exc()
        }), 500
