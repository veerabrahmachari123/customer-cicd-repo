import os
from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

@app.get("/health")
def health():
    try:
        conn = get_db()
        conn.close()
        return jsonify(status="UP", database="UP"), 200
    except Exception as exc:
        return jsonify(status="DOWN", database="DOWN", error=str(exc)), 500

@app.get("/environment")
def environment():
    return jsonify(environment=os.getenv("ENVIRONMENT", "UNKNOWN"))

@app.get("/version")
def version():
    return jsonify(version=os.getenv("APP_VERSION", "UNKNOWN"))

@app.get("/customers")
def customers():
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name, email FROM customers ORDER BY id")
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@app.get("/customers/<int:customer_id>")
def customer(customer_id):
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, name, email FROM customers WHERE id = %s",
                (customer_id,),
            )
            row = cur.fetchone()
            return (jsonify(row), 200) if row else (jsonify(error="Customer not found"), 404)
    finally:
        conn.close()

@app.get("/customers/search")
def search_customers():
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify(error="name query parameter is required"), 400
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, name, email FROM customers WHERE name ILIKE %s ORDER BY id",
                (f"%{name}%",),
            )
            return jsonify(cur.fetchall())
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
