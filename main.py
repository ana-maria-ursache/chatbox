from fastapi import FastAPI, Depends
import uvicorn
from db.model import UserRecord, Todo
from db.database import get_db, Base, engine
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get-users")
def get_users(db: Session = Depends(get_db)):
    return db.query(UserRecord).all()


@app.post("/create-user")
def create_user(name: str, email: str, db: Session = Depends(get_db)):
    new_user = UserRecord(name=name, email=email)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/create-todo")
def create_todo(title: str, description: str, is_completed: bool, user_id: int, db: Session = Depends(get_db)): 
    
    new_todo = Todo(title=title, description=description, is_done=is_completed, user_id=user_id)
    
    if user_id not in [user.id for user in db.query(UserRecord).all()]:
        return {"status": "user not found"}
    
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    
    return new_todo

@app.get("/get-todos")
def get_todos(db: Session = Depends(get_db)):
    return db.query(Todo).all()

@app.get("/get-user-todos")
def get_todos(user_id: int, db: Session = Depends(get_db)):
    todos_query = db.query(Todo)
    done_todos = todos_query.filter(Todo.user_id == user_id)
    return done_todos.all()

@app.delete("/delete-todo")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todos_query = db.query(Todo)
    todo = todos_query.filter(Todo.id == todo_id).first()
    
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
