from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("library.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL DEFAULT 'General',
            status TEXT NOT NULL DEFAULT 'Available'
                CHECK(status IN ('Available', 'Issued'))
        );

        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT
        );

        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL DEFAULT (date('now')),
            return_date TEXT,
            returned INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(member_id) REFERENCES members(id)
        );
        """)


def error(message, status=400):
    return jsonify({"error": message}), status


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/api/dashboard")
def dashboard():
    with get_db() as db:
        total = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        available = db.execute(
            "SELECT COUNT(*) FROM books WHERE status='Available'"
        ).fetchone()[0]
        issued = db.execute(
            "SELECT COUNT(*) FROM books WHERE status='Issued'"
        ).fetchone()[0]
        members = db.execute("SELECT COUNT(*) FROM members").fetchone()[0]
    return jsonify({"total_books": total, "available_books": available,
                    "issued_books": issued, "members": members})


@app.get("/api/books")
def list_books():
    query = request.args.get("q", "").strip()
    with get_db() as db:
        rows = db.execute("""
            SELECT * FROM books
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ?
            ORDER BY id DESC
        """, tuple([f"%{query}%"] * 4)).fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/books")
def add_book():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    isbn = data.get("isbn", "").strip()
    category = data.get("category", "General").strip() or "General"
    if not title or not author or not isbn:
        return error("Title, author and ISBN are required.")
    try:
        with get_db() as db:
            cur = db.execute(
                "INSERT INTO books(title, author, isbn, category) VALUES(?,?,?,?)",
                (title, author, isbn, category)
            )
            book_id = cur.lastrowid
        return jsonify({"message": "Book added successfully.", "id": book_id}), 201
    except sqlite3.IntegrityError:
        return error("That ISBN already exists.")


@app.delete("/api/books/<int:book_id>")
def delete_book(book_id):
    with get_db() as db:
        book = db.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
        if not book:
            return error("Book not found.", 404)
        if book["status"] == "Issued":
            return error("Return this book before deleting it.")
        db.execute("DELETE FROM books WHERE id=?", (book_id,))
    return jsonify({"message": "Book deleted."})


@app.get("/api/members")
def list_members():
    with get_db() as db:
        rows = db.execute("SELECT * FROM members ORDER BY name").fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/members")
def add_member():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    if not name or not email or "@" not in email:
        return error("Enter a name and a valid email address.")
    try:
        with get_db() as db:
            cur = db.execute(
                "INSERT INTO members(name, email, phone) VALUES(?,?,?)",
                (name, email, phone)
            )
            member_id = cur.lastrowid
        return jsonify({"message": "Member added.", "id": member_id}), 201
    except sqlite3.IntegrityError:
        return error("A member with this email already exists.")


@app.get("/api/loans")
def list_loans():
    with get_db() as db:
        rows = db.execute("""
            SELECT loans.id, books.title, books.isbn, members.name AS member,
                   loans.issue_date, loans.returned
            FROM loans
            JOIN books ON books.id=loans.book_id
            JOIN members ON members.id=loans.member_id
            WHERE loans.returned=0
            ORDER BY loans.id DESC
        """).fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/loans")
def issue_book():
    data = request.get_json(silent=True) or {}
    try:
        book_id = int(data.get("book_id"))
        member_id = int(data.get("member_id"))
    except (TypeError, ValueError):
        return error("Choose a book and a member.")
    with get_db() as db:
        book = db.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
        member = db.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
        if not book or not member:
            return error("Book or member not found.", 404)
        if book["status"] != "Available":
            return error("This book is already issued.")
        db.execute("INSERT INTO loans(book_id, member_id) VALUES(?,?)",
                   (book_id, member_id))
        db.execute("UPDATE books SET status='Issued' WHERE id=?", (book_id,))
    return jsonify({"message": "Book issued successfully."}), 201


@app.post("/api/loans/<int:loan_id>/return")
def return_book(loan_id):
    with get_db() as db:
        loan = db.execute(
            "SELECT * FROM loans WHERE id=? AND returned=0", (loan_id,)
        ).fetchone()
        if not loan:
            return error("Active issue record not found.", 404)
        db.execute(
            "UPDATE loans SET returned=1, return_date=date('now') WHERE id=?",
            (loan_id,)
        )
        db.execute("UPDATE books SET status='Available' WHERE id=?",
                   (loan["book_id"],))
    return jsonify({"message": "Book returned successfully."})


@app.get("/api/members/<int:member_id>")
def member_detail(member_id):
    with get_db() as db:
        row = db.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
    if not row:
        return error("Member not found.", 404)
    return jsonify(dict(row))


@app.delete("/api/members/<int:member_id>")
def delete_member(member_id):
    with get_db() as db:
        member = db.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
        if not member:
            return error("Member not found.", 404)
        active = db.execute(
            "SELECT COUNT(*) FROM loans WHERE member_id=? AND returned=0",
            (member_id,)
        ).fetchone()[0]
        if active:
            return error("This member has an active issued book.")
        db.execute("DELETE FROM members WHERE id=?", (member_id,))
    return jsonify({"message": "Member deleted."})


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Endpoint not found."}), 404


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
