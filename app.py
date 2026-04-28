from flask import Flask, render_template, request, jsonify
from chatbot import get_response
import sqlite3

app = Flask(__name__)

# ✅ Function to save user queries in database
def save_query(user_input):
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT
        )
    """)

    # Insert user query
    cursor.execute("INSERT INTO queries (query) VALUES (?)", (user_input,))

    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")

    # ✅ Save query to database
    save_query(user_input)

    # Get chatbot response
    response = get_response(user_input)

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)