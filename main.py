from fastapi import FastAPI
import uvicorn
from db.model import UserRecord, Todo
from db.database import get_db, Base, engine
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/create-user")
def create_user(name: str, email: str):
    db = next(get_db())
    
    try:
        new_user = UserRecord(name=name, email=email)
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    
        return new_user
    finally:
        db.close()

@app.post("/create-todo")
def create_todo(title: str, description: str, user_id: int):
    db = next(get_db())
    try:
        new_todo = Todo(title=title, description=description, user_id=user_id)
        
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        
        return new_todo
    finally:
        db.close()

@app.get("/get-todos")
def get_todos():
    db = next(get_db())
    return db.query(Todo).all()


@app.get("/get-user-todos")
def get_todos(user_id: int):
    db = next(get_db())
    return db.query(Todo).filter(Todo.user_id == user_id).all()

@app.delete("/delete-todo")
def delete_todo(todo_id: int):
    db = next(get_db())
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if todo:
        db.delete(todo)
        db.commit()
        return {"status": "deleted"}
    
    return {"status": "not found"}

# ----------------------------------------
def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
