"""
Limkokwing Library Management API
PROG315 - Object-Oriented Programming 2
Student Assignment - Basic API structure with open-software
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import asyncio
from datetime import datetime, timedelta

app = FastAPI(
    title="Limkokwing Library API",
    description="A basic digital library management system for Limkokwing University Sierra Leone",
    version="1.0.0"
)

# ─────────────────────────────────────────────
# In-memory data store (simulates a database)
# ─────────────────────────────────────────────
books_db: dict[int, dict] = {
    1: {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "category": "Programming", "available": True},
    2: {"id": 2, "title": "Python Crash Course", "author": "Eric Matthes", "category": "Programming", "available": True},
    3: {"id": 3, "title": "Introduction to Algorithms", "author": "Cormen et al.", "category": "Computer Science", "available": False},
    4: {"id": 4, "title": "The Pragmatic Programmer", "author": "Hunt & Thomas", "category": "Programming", "available": True},
    5: {"id": 5, "title": "Design Patterns", "author": "Gang of Four", "category": "Software Engineering", "available": True},
}

borrows_db: dict[int, dict] = {
    1: {
        "borrow_id": 1,
        "user_id": 101,
        "book_id": 3,
        "borrow_date": "2026-03-25",
        "due_date": "2026-04-01",
        "returned": False
    }
}
borrow_counter: int = 2


# ─────────────────────────────────────────────
# Pydantic Models (Request/Response schemas)
# ─────────────────────────────────────────────

class BorrowRequest(BaseModel):
    user_id: int
    book_id: int

class ReturnRequest(BaseModel):
    user_id: int
    book_id: int
    borrow_id: int

class BorrowResponse(BaseModel):
    borrow_id: int
    user_id: int
    book_id: int
    book_title: str
    borrow_date: str
    due_date: str
    message: str

class OverdueRecord(BaseModel):
    borrow_id: int
    user_id: int
    book_id: int
    book_title: str
    due_date: str
    days_overdue: int
    fine_amount_le: float


# ─────────────────────────────────────────────
# ENDPOINT 1: GET /books — Search for books
# ─────────────────────────────────────────────

@app.get("/books", summary="Search books by title, author, or category")
async def get_books(
    title: Optional[str] = Query(None, description="Filter by book title"),
    author: Optional[str] = Query(None, description="Filter by author name"),
    category: Optional[str] = Query(None, description="Filter by category")
) -> dict:
    results = list(books_db.values())
    if title:
        results = [b for b in results if title.lower() in b["title"].lower()]
    if author:
        results = [b for b in results if author.lower() in b["author"].lower()]
    if category:
        results = [b for b in results if category.lower() in b["category"].lower()]
    return {"total_found": len(results), "books": results}


# ─────────────────────────────────────────────
# ENDPOINT 2: POST /borrow — Borrow a book
# ─────────────────────────────────────────────

@app.post("/borrow", summary="Borrow a book from the library")
async def borrow_book(request: BorrowRequest) -> BorrowResponse:
    global borrow_counter
    book = books_db.get(request.book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with ID {request.book_id} not found.")
    if not book["available"]:
        raise HTTPException(status_code=409, detail=f"'{book['title']}' is currently not available.")
    await asyncio.sleep(0.1)
    borrow_date = datetime.today()
    due_date = borrow_date + timedelta(days=14)
    borrow_record = {
        "borrow_id": borrow_counter,
        "user_id": request.user_id,
        "book_id": request.book_id,
        "borrow_date": borrow_date.strftime("%Y-%m-%d"),
        "due_date": due_date.strftime("%Y-%m-%d"),
        "returned": False
    }
    borrows_db[borrow_counter] = borrow_record
    books_db[request.book_id]["available"] = False
    borrow_counter += 1
    return BorrowResponse(
        borrow_id=borrow_record["borrow_id"],
        user_id=request.user_id,
        book_id=request.book_id,
        book_title=book["title"],
        borrow_date=borrow_record["borrow_date"],
        due_date=borrow_record["due_date"],
        message=f"Successfully borrowed '{book['title']}'. Please return by {borrow_record['due_date']}."
    )


# ─────────────────────────────────────────────
# ENDPOINT 3: POST /return — Return a book
# ─────────────────────────────────────────────

@app.post("/return", summary="Return a borrowed book")
async def return_book(request: ReturnRequest) -> dict:
    record = borrows_db.get(request.borrow_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Borrow record ID {request.borrow_id} not found.")
    if record["user_id"] != request.user_id or record["book_id"] != request.book_id:
        raise HTTPException(status_code=403, detail="Borrow record does not match provided user or book.")
    if record["returned"]:
        raise HTTPException(status_code=400, detail="This book has already been returned.")
    await asyncio.sleep(0.1)
    record["returned"] = True
    books_db[request.book_id]["available"] = True
    return {
        "message": f"Book ID {request.book_id} successfully returned.",
        "borrow_id": request.borrow_id,
        "returned_on": datetime.today().strftime("%Y-%m-%d")
    }


# ─────────────────────────────────────────────
# ENDPOINT 4: GET /overdue — Track overdue books and fines
# ─────────────────────────────────────────────

@app.get("/overdue", summary="Get overdue books and calculate fines")
async def get_overdue_books() -> dict:
    fine_per_day: float = 5.0
    today = datetime.today().date()
    overdue_list: list[OverdueRecord] = []
    for record in borrows_db.values():
        if record["returned"]:
            continue
        due_date = datetime.strptime(record["due_date"], "%Y-%m-%d").date()
        if today > due_date:
            days_overdue = (today - due_date).days
            book = books_db.get(record["book_id"], {})
            overdue_list.append(OverdueRecord(
                borrow_id=record["borrow_id"],
                user_id=record["user_id"],
                book_id=record["book_id"],
                book_title=book.get("title", "Unknown"),
                due_date=record["due_date"],
                days_overdue=days_overdue,
                fine_amount_le=round(days_overdue * fine_per_day, 2)
            ))
    return {
        "total_overdue": len(overdue_list),
        "fine_rate_per_day_NLe": fine_per_day,
        "overdue_records": [r.dict() for r in overdue_list]
    }


@app.get("/")
async def root() -> dict:
    return {"message": "Welcome to the Limkokwing Library API", "version": "1.0.0", "docs": "/docs"}


# ─────────────────────────────────────────────
# PART B: Async simulation of multiple users
# ─────────────────────────────────────────────

async def simulate_user_borrow(user_id: int, book_id: int) -> str:
    await asyncio.sleep(0.05)
    book = books_db.get(book_id)
    if book and book["available"]:
        books_db[book_id]["available"] = False
        return f"User {user_id} successfully borrowed '{book['title']}'"
    elif book:
        return f"User {user_id} could NOT borrow '{book['title']}' — already taken"
    return f"User {user_id}: Book {book_id} not found"


async def simulate_multiple_users() -> None:
    print("\n=== Simulating Multiple Concurrent Users ===\n")
    books_db[4]["available"] = True
    books_db[5]["available"] = True
    tasks = [
        simulate_user_borrow(user_id=201, book_id=4),
        simulate_user_borrow(user_id=202, book_id=4),
        simulate_user_borrow(user_id=203, book_id=5),
        simulate_user_borrow(user_id=204, book_id=5),
        simulate_user_borrow(user_id=205, book_id=1),
    ]
    results = await asyncio.gather(*tasks)
    for result in results:
        print(f"  → {result}")
    print("\n=== Simulation Complete ===\n")


if __name__ == "__main__":
    import uvicorn
    asyncio.run(simulate_multiple_users())
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
