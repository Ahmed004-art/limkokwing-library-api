# Limkokwing Library Management API

**PROG315 – Object-Oriented Programming 2**  
**Assignment:** Basic API structure with open-software  
**Institution:** Limkokwing University of Creative Technology – Sierra Leone  

---

## Project Description

A RESTful API built with **Python FastAPI** that provides a digital library management system for Limkokwing University. It enables students and staff to search books, borrow and return items, and track overdue fines — while supporting multiple concurrent users via asynchronous programming.

---

## Features

| Endpoint | Method | Description |
|---|---|---|
| `/books` | GET | Search books by title, author, or category |
| `/borrow` | POST | Borrow an available book |
| `/return` | POST | Return a borrowed book |
| `/overdue` | GET | View overdue books and calculated fines |

---

## Tech Stack

- **Python 3.11+**
- **FastAPI** – web framework
- **Uvicorn** – ASGI server
- **Pydantic** – data validation and type annotations
- **asyncio** – concurrent multi-user simulation

---

## Setup & Run

```bash
# Install dependencies
pip install fastapi uvicorn

# Run the API server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit **http://localhost:8000/docs** for the interactive Swagger UI.

---

## SDG Alignment

**SDG 4 – Quality Education**: This API supports accessible, efficient library services that enable students to find and borrow educational resources, directly contributing to improved learning outcomes.

---

## Author

Student – Faculty of Information and Communication Technology  
Semester 04 | March 2026 – July 2026
