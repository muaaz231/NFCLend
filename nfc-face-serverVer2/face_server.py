from flask import Flask, request, jsonify
from face_engine import verify_face_from_camera, encode_face_from_camera
import json
import psycopg2
import psycopg2.extras
import time
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import shutil
import os
from pathlib import Path





app = Flask(__name__)
lock_current_scan = threading.Lock() #this just makes sure 2 requests dont try updating  same time
current_scan = {"uid": None, "ts": 0}

# Optional: load settings from a .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Credentials come from environment variables (see .env.example) so they never get committed
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
FACE_DATA_DIR = Path(__file__).parent / "face_data"

def get_db():
    return psycopg2.connect(
        dbname=os.environ.get("DB_NAME", "nfcproject"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", ""),
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 5432))
    )

def send_email(to_email, subject, body): #this basicaly handles the email sending from the host email
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "server running"})

@app.route("/register-face", methods=["POST"])
def register_face():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        frames = data.get("frames", 15)
        print(f"Registering face for: {user_id}")
        result = encode_face_from_camera(user_id, frames_to_capture=frames)
        parsed = json.loads(result)
        if parsed.get("success"):
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET face_encoding_date = NOW() WHERE nfc_id = %s",
                (user_id,)
            )
            conn.commit()
            conn.close()
        return jsonify(parsed)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/verify-face", methods=["POST"])
def verify_face():
    try:
        time.sleep(0.5)
        data = request.get_json()
        user_id = data.get("user_id")
        frames = data.get("frames", 8)
        print(f"Verifying face for: {user_id}")
        result = verify_face_from_camera(user_id, frames_to_capture=frames)
        parsed = json.loads(result)
        print(f"verified={parsed.get('verified')} confidence={parsed.get('confidence')}")
        if user_id:
            try:
                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT id FROM users WHERE nfc_id = %s AND is_deleted = FALSE", (user_id,))
                row = cur.fetchone()
                if row:
                    cur.execute(
                        "INSERT INTO face_logs (user_id, verification_result, match_confidence) VALUES (%s, %s, %s)",
                        (row[0], parsed.get("verified"), parsed.get("confidence"))
                    )
                    conn.commit()
                conn.close()
            except Exception:
                pass
        return jsonify(parsed)
    except Exception as e:
        return jsonify({"success": False, "verified": False, "message": str(e)}), 500


@app.route("/delete-face/<nfc_id>", methods=["DELETE"])
def delete_face(nfc_id):
    try:
        user_face_dir = FACE_DATA_DIR / f"user_{nfc_id}"
        if user_face_dir.exists():
            shutil.rmtree(user_face_dir)
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET face_encoding_date = NULL WHERE nfc_id = %s", (nfc_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
@app.route("/email/rental-confirmation", methods=["POST"])
def send_rental_confirmation():
    try:
        data = request.get_json()
        to_email = data.get("email")
        user_name = data.get("user_name")
        item_name = data.get("item_name")
        subject = "Rental Confirmation — Equipment Checkout"
        body = (
            f"Hi {user_name},\n\n"
            f"This confirms you have successfully checked out: {item_name}\n\n"
            f"Please return it when you are finished. Late returns may incur a fee.\n\n"
            f"Thank you for using our equipment lending system."
        )
        ok = send_email(to_email, subject, body)
        return jsonify({"success": ok})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/email/return-confirmation", methods=["POST"])
def send_return_confirmation():
    try:
        data = request.get_json()
        to_email = data.get("email")
        user_name = data.get("user_name")
        item_name = data.get("item_name")
        rating = data.get("rating")
        subject = "Return Confirmation — Equipment Returned"
        rating_line = f"\nYour experience rating for this item: {rating}/10\n" if rating else ""
        body = (
            f"Hi {user_name},\n\n"
            f"This confirms that you have successfully returned: {item_name}\n"
            f"{rating_line}\n"
            f"Thank you for returning the item promptly. Your record has been updated.\n\n"
            f"Equipment Lending System"
        )
        ok = send_email(to_email, subject, body)
        return jsonify({"success": ok})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/email/reminder", methods=["POST"])
def send_reminder():
    try:
        data = request.get_json()
        to_email = data.get("email")
        user_name = data.get("user_name")
        item_name = data.get("item_name")
        subject = "Equipment Return Reminder"
        body = (
            f"Hi {user_name},\n\n"
            f"This is a reminder that you still have checked out: {item_name}\n\n"
            f"Please return it as soon as possible.\n\n"
            f"Equipment Lending System"
        )
        ok = send_email(to_email, subject, body)
        return jsonify({"success": ok})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500




@app.route("/email/manual", methods=["POST"])
def send_manual_email():
    try:
        data = request.get_json()
        to_email = data.get("to_email")
        subject = data.get("subject", "Message from Equipment System")
        body = data.get("body", "")
        if not to_email or not body:
            return jsonify({"success": False, "error": "to_email and body are required"}), 400
        ok = send_email(to_email, subject, body)
        return jsonify({"success": ok})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/user/<nfc_id>", methods=["GET"])
def get_user(nfc_id):
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM users WHERE nfc_id = %s AND is_deleted = FALSE", (nfc_id,))
        user = cur.fetchone()
        conn.close()
        if user:
            return jsonify({"found": True, "user": dict(user)})
        return jsonify({"found": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/user", methods=["POST"]) #this helps with user creation and keeping records even if the user is deleted
def create_user():
    try:
        data = request.get_json()
        conn = get_db()
        cur = conn.cursor()
        nfc_id = data["nfc_id"]
        
        cur.execute("SELECT id, is_deleted FROM users WHERE nfc_id = %s", (nfc_id,))
        existing = cur.fetchone()
        
        if existing:
            if existing[1]: 
                cur.execute(
                    "UPDATE users SET name = %s, email = %s, role = %s, password = %s, is_deleted = FALSE WHERE nfc_id = %s",
                    (data["name"], data.get("email", ""), data.get("role", "student"), data.get("password", ""), nfc_id)
                )
            else:
                conn.close()
                return jsonify({"success": False, "error": "User already exists"}), 400
        else:
            cur.execute(
                "INSERT INTO users (name, email, nfc_id, role, password, is_deleted) VALUES (%s, %s, %s, %s, %s, FALSE)",
                (data["name"], data.get("email", ""), nfc_id, data.get("role", "student"), data.get("password", ""))
            )
        
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/user/<nfc_id>", methods=["DELETE"])
def delete_user(nfc_id):
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT rented_item_uid FROM users WHERE nfc_id = %s AND is_deleted = FALSE", (nfc_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return jsonify({"success": False, "error": "User not found"}), 404
        if row["rented_item_uid"]:
            conn.close()
            return jsonify({"success": False, "error": "User has an item currently rented. Return it first."}), 400
        cur.execute("UPDATE users SET is_deleted = TRUE WHERE nfc_id = %s", (nfc_id,))
        conn.commit()
        conn.close()
        user_face_dir = FACE_DATA_DIR / f"user_{nfc_id}"
        if user_face_dir.exists():
            shutil.rmtree(user_face_dir)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/user/<nfc_id>/password", methods=["PATCH"])
def change_password(nfc_id):
    try:
        data = request.get_json()
        new_password = data.get("password")
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password = %s WHERE nfc_id = %s AND is_deleted = FALSE", (new_password, nfc_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/user/<nfc_id>/profile", methods=["PATCH"])
def update_profile(nfc_id):
    try:
        data = request.get_json()
        new_name = data.get("name")
        new_email = data.get("email")
        new_password = data.get("password")
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if new_name:
            cur.execute(
                "SELECT id FROM users WHERE name = %s AND nfc_id != %s AND is_deleted = FALSE",
                (new_name, nfc_id)
            )
            clash = cur.fetchone()
            if clash:
                conn.close()
                return jsonify({"success": False, "error": "That username is already taken by another user."}), 409
        fields = []
        values = []
        if new_name:
            fields.append("name = %s")
            values.append(new_name)
        if new_email is not None:
            fields.append("email = %s")
            values.append(new_email)
        if new_password:
            fields.append("password = %s")
            values.append(new_password)
        if not fields:
            conn.close()
            return jsonify({"success": False, "error": "Nothing to update"}), 400
        values.append(nfc_id)
        cur.execute(f"UPDATE users SET {', '.join(fields)} WHERE nfc_id = %s AND is_deleted = FALSE", values)
        conn.commit()
        cur.execute("SELECT * FROM users WHERE nfc_id = %s", (nfc_id,))
        updated = cur.fetchone()
        conn.close()
        return jsonify({"success": True, "user": dict(updated)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/users", methods=["GET"]) 
def get_all_users():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM users WHERE is_deleted = FALSE")
        users = cur.fetchall()
        conn.close()
        return jsonify([dict(u) for u in users])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/user/<nfc_id>/rented-item", methods=["PATCH"])
def update_rented_item(nfc_id):
    try:
        data = request.get_json()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET rented_item_uid = %s WHERE nfc_id = %s AND is_deleted = FALSE",
            (data.get("rented_item_uid"), nfc_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/equipment", methods=["GET"])
def get_all_equipment():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM equipment WHERE is_deleted = FALSE")
        items = cur.fetchall()
        conn.close()
        return jsonify([dict(i) for i in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/equipment/<nfc_tag>", methods=["GET"])
def get_equipment(nfc_tag):
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM equipment WHERE nfc_tag = %s AND is_deleted = FALSE", (nfc_tag,))
        item = cur.fetchone()
        conn.close()
        if item:
            return jsonify({"found": True, "item": dict(item)})
        return jsonify({"found": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/equipment", methods=["POST"])
def add_equipment():
    try:
        data = request.get_json()
        conn = get_db()
        cur = conn.cursor()
        nfc_tag = data["nfc_tag"]
        
        cur.execute("SELECT id, is_deleted FROM equipment WHERE nfc_tag = %s", (nfc_tag,))
        existing = cur.fetchone()
        
        if existing:
            if existing[1]: 
                cur.execute(
                    "UPDATE equipment SET name = %s, category = %s, status = 'available', is_deleted = FALSE WHERE nfc_tag = %s",
                    (data["name"], data.get("category", ""), nfc_tag)
                )
            else:
                conn.close()
                return jsonify({"success": False, "error": "Equipment already exists"}), 400
        else:
            cur.execute(
                "INSERT INTO equipment (name, category, nfc_tag, status, is_deleted) VALUES (%s, %s, %s, 'available', FALSE)",
                (data["name"], data.get("category", ""), nfc_tag)
            )
        
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/equipment/<nfc_tag>", methods=["DELETE"])
def delete_equipment(nfc_tag):
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT status FROM equipment WHERE nfc_tag = %s AND is_deleted = FALSE", (nfc_tag,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return jsonify({"success": False, "error": "Equipment not found"}), 404
        if row["status"] == "rented":
            conn.close()
            return jsonify({"success": False, "error": "Item is currently rented out"}), 400
        cur.execute("UPDATE equipment SET is_deleted = TRUE WHERE nfc_tag = %s", (nfc_tag,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/equipment/<nfc_tag>/checkout", methods=["PATCH"])
def checkout_item(nfc_tag):
    try:
        data = request.get_json()
        user_nfc = data.get("user_nfc")
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, name, email FROM users WHERE nfc_id = %s AND is_deleted = FALSE", (user_nfc,))
        user = cur.fetchone()
        cur.execute("SELECT id, name, category FROM equipment WHERE nfc_tag = %s AND is_deleted = FALSE", (nfc_tag,))
        equip = cur.fetchone()
        if not user or not equip:
            conn.close()
            return jsonify({"success": False, "error": "user or equipment not found"}), 404
        cur.execute("UPDATE equipment SET status = 'rented' WHERE nfc_tag = %s", (nfc_tag,))
        cur.execute("UPDATE users SET rented_item_uid = %s WHERE nfc_id = %s", (nfc_tag, user_nfc))
        cur.execute(
            "INSERT INTO transactions (user_id, equipment_id, face_verified) VALUES (%s, %s, TRUE)",
            (user["id"], equip["id"])
        )
        conn.commit()
        conn.close()
        if user.get("email"):
            subject = "Rental Confirmation — Equipment Checkout"
            body = (
                f"Hi {user['name']},\n\n"
                f"This confirms you have successfully checked out: {equip['name']}\n"
                f"Category: {equip['category']}\n\n"
                f"Please return it within 2 weeks. Late returns may incur a fee.\n\n"
                f"Thank you for using our equipment lending system."
            )
            send_email(user["email"], subject, body)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/equipment/<nfc_tag>/return", methods=["PATCH"])
def return_item(nfc_tag):
    try:
        data = request.get_json()
        user_nfc = data.get("user_nfc")
        rating = data.get("rating")
        condition_report = data.get("condition_report")
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, name, email FROM users WHERE nfc_id = %s AND is_deleted = FALSE", (user_nfc,))
        user = cur.fetchone()
        cur.execute("SELECT id, name, category FROM equipment WHERE nfc_tag = %s AND is_deleted = FALSE", (nfc_tag,))
        equip = cur.fetchone()
        if not user or not equip:
            conn.close()
            return jsonify({"success": False, "error": "user or equipment not found"}), 404
        cur.execute("UPDATE equipment SET status = 'available' WHERE nfc_tag = %s", (nfc_tag,))
        cur.execute("UPDATE users SET rented_item_uid = NULL WHERE nfc_id = %s", (user_nfc,))
        if rating is not None:
            cur.execute(
                """UPDATE transactions SET return_time = NOW(), rating = %s, condition_report = %s
                   WHERE user_id = %s AND equipment_id = %s AND return_time IS NULL""",
                (rating, condition_report, user["id"], equip["id"])
            )
            cur.execute(
                """UPDATE equipment SET
                   avg_rating = (SELECT AVG(rating) FROM transactions WHERE equipment_id = %s AND rating IS NOT NULL),
                   rating_count = (SELECT COUNT(*) FROM transactions WHERE equipment_id = %s AND rating IS NOT NULL)
                   WHERE id = %s""",
                (equip["id"], equip["id"], equip["id"])
            )
        else:
            cur.execute(
                """UPDATE transactions SET return_time = NOW(), condition_report = %s
                   WHERE user_id = %s AND equipment_id = %s AND return_time IS NULL""",
                (condition_report, user["id"], equip["id"])
            )
        conn.commit()
        conn.close()
        if user.get("email"):
            subject = "Return Confirmation — Equipment Returned"
            body = (
                f"Hi {user['name']},\n\n"
                f"This confirms that you have successfully returned: {equip['name']}\n"
                f"Category: {equip['category']}\n\n"
                f"Thank you for returning the item promptly. Your record has been updated.\n\n"
                f"Equipment Lending System"
            )
            send_email(user["email"], subject, body)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/equipment/<nfc_tag>/admin-return", methods=["PATCH"])
def admin_return_item(nfc_tag):
    try:
        data = request.get_json()
        condition_report = data.get("condition_report", "Returned by admin")
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, nfc_id, name, email FROM users WHERE rented_item_uid = %s AND is_deleted = FALSE", (nfc_tag,))
        user = cur.fetchone()
        cur.execute("SELECT id, name FROM equipment WHERE nfc_tag = %s AND is_deleted = FALSE", (nfc_tag,))
        equip = cur.fetchone()
        if not equip:
            conn.close()
            return jsonify({"success": False, "error": "Equipment not found"}), 404
        if not user:
            conn.close()
            return jsonify({"success": False, "error": "No user currently has this item checked out"}), 400
        cur.execute("UPDATE equipment SET status = 'available' WHERE nfc_tag = %s", (nfc_tag,))
        cur.execute("UPDATE users SET rented_item_uid = NULL WHERE nfc_id = %s", (user["nfc_id"],))
        cur.execute(
            """UPDATE transactions SET return_time = NOW(), condition_report = %s
               WHERE user_id = %s AND equipment_id = %s AND return_time IS NULL""",
            (condition_report, user["id"], equip["id"])
        )
        conn.commit()
        conn.close()
        return jsonify({
            "success": True,
            "user_name": user["name"],
            "user_email": user["email"],
            "item_name": equip["name"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/stats/hot-items", methods=["GET"])
def hot_items():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT e.name, e.category, e.status,
                   COALESCE(e.avg_rating, 0) as avg_rating,
                   COALESCE(e.rating_count, 0) as rating_count,
                   COUNT(t.id) as total_rentals
            FROM equipment e
            LEFT JOIN transactions t ON e.id = t.equipment_id
            WHERE e.is_deleted = FALSE
            GROUP BY e.id, e.name, e.category, e.status, e.avg_rating, e.rating_count
            ORDER BY total_rentals DESC, avg_rating DESC
        """)
        rows = cur.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/stats/summary", methods=["GET"])
def summary_stats():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT COUNT(*) as total FROM users WHERE role != 'admin' AND is_deleted = FALSE")
        users = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(*) as total FROM equipment WHERE is_deleted = FALSE")
        equip_total = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(*) as total FROM equipment WHERE status = 'rented' AND is_deleted = FALSE")
        equip_rented = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(*) as total FROM transactions")
        tx_total = cur.fetchone()["total"]
        conn.close()
        return jsonify({
            "users": users,
            "equipment_total": equip_total,
            "equipment_rented": equip_rented,
            "total_transactions": tx_total
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/history", methods=["GET"])
def get_all_history():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT t.id, t.checkout_time, t.return_time, t.face_verified, t.rating,
                   t.condition_report,
                   u.name as user_name, u.email as user_email,
                   e.name as item_name, e.category as item_category
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            JOIN equipment e ON t.equipment_id = e.id
            ORDER BY t.checkout_time DESC
        """)
        rows = cur.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/history/user/<nfc_id>", methods=["GET"]) #helps with user history, transaction ratings etc
def get_user_history(nfc_id):
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT t.id, t.checkout_time, t.return_time, t.rating, t.condition_report,
                   e.name as item_name, e.category as item_category
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            JOIN equipment e ON t.equipment_id = e.id
            WHERE u.nfc_id = %s
            ORDER BY t.checkout_time DESC
        """, (nfc_id,))
        rows = cur.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/notify-scan", methods=["POST"])
def notify_scan():
    data = request.get_json()
    with lock_current_scan:
        current_scan["uid"] = data.get("uid")
        current_scan["ts"] = time.time()
    return jsonify({"received": True})

@app.route("/current-scan", methods=["GET"])
def get_current_scan():
    with lock_current_scan:
        if time.time() - current_scan["ts"] > 30:
            return jsonify({"uid": None})
        return jsonify({"uid": current_scan["uid"]})

@app.route("/current-scan", methods=["DELETE"])
def clear_scan():
    with lock_current_scan:
        current_scan["uid"] = None
        current_scan["ts"] = 0
    return jsonify({"cleared": True})

if __name__ == "__main__":
    print("Starting NFC Face Server on port 5001...")
    app.run(host="0.0.0.0", port=5001, debug=True)
