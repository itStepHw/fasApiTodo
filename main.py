from pydantic import BaseModel
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from database import ToDoItem, get_db

app = FastAPI()


class Create(BaseModel):
    title: str
    description: Optional[str] = None


class Update(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class Response(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool



@app.post("/todos/", response_model=Response)
def create_todo(todo: Create, db: Session = Depends(get_db)):
    db_todo = ToDoItem(title=todo.title, description=todo.description)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.get("/todos/", response_model=List[Response])
def read_todos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    todos = db.query(ToDoItem).offset(skip).limit(limit).all()
    return todos


@app.get("/todos/{todo_id}", response_model=Response)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(ToDoItem).filter(ToDoItem.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="ToDo not found")
    return todo


@app.put("/todos/{todo_id}", response_model=Response)
def update_todo(todo_id: int, todo: Update, db: Session = Depends(get_db)):
    db_todo = db.query(ToDoItem).filter(ToDoItem.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="ToDo not found")

    if todo.title is not None:
        db_todo.title = todo.title
    if todo.description is not None:
        db_todo.description = todo.description
    if todo.completed is not None:
        db_todo.completed = todo.completed

    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.delete("/todos/{todo_id}", response_model=Response)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(ToDoItem).filter(ToDoItem.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="ToDo not found")

    db.delete(db_todo)
    db.commit()
    return db_todo
