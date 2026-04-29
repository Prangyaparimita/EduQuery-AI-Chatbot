from flask import Flask, render_template, request, jsonify, session
import sqlite3
import os
from chatbot import get_response

app = Flask(__name__)
app.secret_key = "eduquery_secret_key_2024"  # needed for session

# ✅ Initialize Database
def init_db():
    if os.path.exists("chatbot.db"):
        try:
            conn = sqlite3.connect("chatbot.db")
            conn.execute("SELECT 1")
            conn.close()
        except:
            os.remove("chatbot.db")

    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        intent TEXT,
        response TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ✅ Home Page
@app.route("/")
def home():
    # Always start fresh on every page load
    session.clear()
    return render_template("index.html")

# ✅ Chat API
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"response": "Please type a message!"})

        # Store query in DB
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO queries (query) VALUES (?)", (user_input,))
        conn.commit()
        conn.close()

        # Restore memory from session into chatbot module
        import chatbot as chatbot_module
        chatbot_module.current_course      = session.get("current_course", None)
        chatbot_module.awaiting_course_for = session.get("awaiting_course_for", None)

        # Get response
        response = get_response(user_input)

        # Save updated memory back to session
        session["current_course"]      = chatbot_module.current_course
        session["awaiting_course_for"] = chatbot_module.awaiting_course_for
        session.modified = True  # force Flask to persist session changes

        return jsonify({"response": response})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"response": "Sorry, a server error occurred. Please try again."})

# ✅ Admin Panel
@app.route("/admin", methods=["GET", "POST"])
def admin():
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()

    if request.method == "POST":
        intent = request.form.get("intent", "").strip()
        response = request.form.get("response", "").strip()

        if intent and response:
            cursor.execute(
                "INSERT INTO responses (intent, response) VALUES (?, ?)",
                (intent, response)
            )
            conn.commit()

    cursor.execute("SELECT * FROM responses")
    data = cursor.fetchall()
    conn.close()

    return render_template("admin.html", data=data)

# ✅ Admin Delete
@app.route("/admin/delete/<int:row_id>", methods=["POST"])
def admin_delete(row_id):
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM responses WHERE id=?", (row_id,))
    conn.commit()
    conn.close()
    from flask import redirect, url_for
    return redirect(url_for("admin"))

# ✅ Admin Edit
@app.route("/admin/edit/<int:row_id>", methods=["POST"])
def admin_edit(row_id):
    intent = request.form.get("intent", "").strip()
    response = request.form.get("response", "").strip()
    if intent and response:
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE responses SET intent=?, response=? WHERE id=?",
            (intent, response, row_id)
        )
        conn.commit()
        conn.close()
    from flask import redirect, url_for
    return redirect(url_for("admin"))

# ✅ Dashboard
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT query, COUNT(*) as count
    FROM queries
    GROUP BY query
    ORDER BY count DESC
    """)
    data = cursor.fetchall()
    conn.close()

    # Return as formatted HTML instead of raw string
    rows = "".join(f"<tr><td>{q}</td><td>{c}</td></tr>" for q, c in data)
    return f"""
    <html><head><title>Dashboard</title>
    <style>body{{font-family:sans-serif;padding:20px}} table{{border-collapse:collapse;width:100%}} 
    th,td{{border:1px solid #ddd;padding:8px;text-align:left}} th{{background:#4CAF50;color:white}}</style>
    </head><body>
    <h2>📊 Query Dashboard</h2>
    <table><tr><th>Query</th><th>Count</th></tr>{rows}</table>
    </body></html>
    """

# ✅ Run App
if __name__ == "__main__":
    app.run(debug=True)
