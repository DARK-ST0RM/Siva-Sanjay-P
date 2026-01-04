from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_FILE = "database.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consultant TEXT,
            date TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT,
            booked_by TEXT,
            requested_at TEXT
        )
    """)
    conn.commit()
    conn.close()

create_table()

# ----------------- Create Slot (Consultant) -----------------
@app.route("/api/slots", methods=["POST"])
def create_slot():
    data = request.json
    consultant = data.get("consultant")
    date = data.get("date")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    
    if not consultant or not date or not start_time or not end_time:
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO slots (consultant, date, start_time, end_time, status) VALUES (?, ?, ?, ?, ?)",
        (consultant, date, start_time, end_time, "available")
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Slot created successfully"})


# ----------------- List Slots -----------------
@app.route("/api/slots", methods=["GET"])
def list_slots():
    consultant_filter = request.args.get("consultant")
    conn = get_db()
    if consultant_filter:
        slots = conn.execute("SELECT * FROM slots WHERE consultant = ?", (consultant_filter,)).fetchall()
    else:
        slots = conn.execute("SELECT * FROM slots").fetchall()
    conn.close()
    return jsonify([dict(slot) for slot in slots])


# ----------------- Client requests booking -----------------
@app.route("/api/slots/<int:slot_id>/request", methods=["POST"])
def request_booking(slot_id):
    data = request.json
    client_username = data.get("client_username")

    conn = get_db()
    slot = conn.execute("SELECT * FROM slots WHERE id = ?", (slot_id,)).fetchone()
    if not slot:
        return jsonify({"error": "Slot not found"}), 404
    if slot["status"] != "available":
        return jsonify({"error": f"Cannot request booking, slot is {slot['status']}"}), 400

    conn.execute(
        "UPDATE slots SET status='pending', booked_by=?, requested_at=? WHERE id=?",
        (client_username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), slot_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Booking requested successfully"})


# ----------------- Consultant confirms booking -----------------
@app.route("/api/slots/<int:slot_id>/confirm", methods=["POST"])
def confirm_booking(slot_id):
    conn = get_db()
    slot = conn.execute("SELECT * FROM slots WHERE id = ?", (slot_id,)).fetchone()
    if not slot:
        return jsonify({"error": "Slot not found"}), 404
    if slot["status"] != "pending":
        return jsonify({"error": f"Cannot confirm, slot is {slot['status']}"}), 400

    conn.execute(
        "UPDATE slots SET status='booked' WHERE id=?",
        (slot_id,)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Slot confirmed successfully"})


if __name__ == "__main__":
    app.run(debug=True)
