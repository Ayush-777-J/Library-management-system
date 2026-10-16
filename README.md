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
