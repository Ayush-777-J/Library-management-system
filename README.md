# Libra — Library Management System

A mini full-stack Library Management System built with HTML, CSS, JavaScript, Python Flask and SQLite.

## Features
- Dashboard with total, available and issued book counts, plus member count
- Add, list, search and delete books
- Register and list members
- Issue an available book to a registered member
- Return an issued book
- Validation for duplicate ISBN/email and unavailable books
- SQLite database is created automatically on first run

## Requirements
- Python 3.9+
- pip

## Run locally (Windows PowerShell)

1. Open this folder in VS Code.
2. Create a virtual environment:
   ```powershell
   python -m venv venv
   ```
3. Activate it:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt:
   ```cmd
   venv\Scripts\activate.bat
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   python app.py
   ```
6. Open http://127.0.0.1:5000 in your browser.

The `library.db` SQLite file and its tables are created automatically when the app starts.

## Main API routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/dashboard` | Dashboard counts |
| GET | `/api/books?q=` | List/search books |
| POST | `/api/books` | Add a book |
| DELETE | `/api/books/<id>` | Delete an available book |
| GET | `/api/members` | List members |
| POST | `/api/members` | Register a member |
| DELETE | `/api/members/<id>` | Delete a member with no active loan |
| GET | `/api/loans` | List active loans |
| POST | `/api/loans` | Issue a book |
| POST | `/api/loans/<id>/return` | Return a book |

## GitHub

Create a GitHub repository, then from this project folder run:

```bash
git init
git add .
git commit -m "Initial library management system"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

Do not commit the virtual environment or generated database. They are excluded by `.gitignore`.

## Before submission
- Test adding a book, searching, registering a member, issuing and returning a book.
- Test duplicate ISBN/email and trying to issue an already-issued book.
- Add your name, roll number and course details here if your teacher requires them.
- Take screenshots of the working application for your project documentation.
