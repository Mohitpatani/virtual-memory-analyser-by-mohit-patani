# app.py
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from memory_manager import MemoryManager
from process import Process
from config import PAGE_TABLE_SIZE, FRAME_COUNT

app = Flask(__name__)
CORS(app)

# Start with defaults from config.py
memory_manager = MemoryManager(algorithm_name="FIFO", frame_count=FRAME_COUNT)
process = Process(memory_manager)


@app.route("/")
def index():
    return render_template("index.html", page_table_size=PAGE_TABLE_SIZE, current_algorithm=memory_manager.algorithm_name)


@app.route("/state", methods=["GET"])
def get_state():
    return jsonify(memory_manager.get_state())


@app.route("/access", methods=["POST"])
def access_page():
    data = request.get_json(force=True)
    page = data.get("page")
    if page is None:
        return jsonify({"error": "Missing 'page'"}), 400
    try:
        page = int(page)
    except Exception:
        return jsonify({"error": "Page must be integer"}), 400

    try:
        state = memory_manager.access_page(page)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 500

    return jsonify(state)


@app.route("/set_algorithm", methods=["POST"])
def set_algorithm():
    data = request.get_json(force=True)
    algorithm = data.get("algorithm")
    frame_count = data.get("frame_count")  # optional: override frame count
    reference_string = data.get("reference_string")

    try:
        fc = None
        if frame_count is not None:
            fc = int(frame_count)
            if fc <= 0:
                raise ValueError("frame_count must be positive")
    except Exception as e:
        return jsonify({"error": f"Invalid frame_count: {e}"}), 400

    try:
        memory_manager.set_algorithm(algorithm, frame_count=fc, reference_string=reference_string)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"status": "ok", "algorithm": memory_manager.algorithm_name, "frame_count": memory_manager.frame_count, "state": memory_manager.get_state()})


@app.route("/simulate", methods=["POST"])
def simulate_sequence():
    data = request.get_json(force=True)
    seq = data.get("sequence")
    if not isinstance(seq, list):
        return jsonify({"error": "Missing or invalid 'sequence' list"}), 400
    try:
        seq = [int(x) for x in seq]
    except Exception:
        return jsonify({"error": "sequence must be list of integers"}), 400

    total_faults = process.simulate(seq)
    return jsonify({"total_faults": total_faults, "final_state": memory_manager.get_state(), "sequence": seq})


@app.route("/reset", methods=["POST"])
def reset():
    memory_manager.reset()
    return jsonify({"status": "ok", "state": memory_manager.get_state()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
