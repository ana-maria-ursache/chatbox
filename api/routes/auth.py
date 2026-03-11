from fastapi import APIRouter, Depends, HTTPException, status
from db.database import get_db
from db.model import UserRecord
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timedelta, timezone
from ..Settings import settings
import bcrypt
import jwt

router = APIRouter(prefix="/auth", tags=["auth"])

# models
class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=5, max_length=20)
    avatar_url: str = Field(default="") # optional
    password_hash: str = Field(min_length=8, max_length=20)

class User(BaseModel):
    id: int
    email: EmailStr
    name: str
    avatar_url: str
    password_hash: str
    
    # When validating a model from a non‑dict 
    # object, read values from its attributes.
    model_config = {
        "from_attributes": True
    }

class TokenResponse(BaseModel):
    user: User
    access_token: str
    token_type: str = "bearer"

# helper functions
def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

# general user - for testing
user_create = UserCreate(
    email="anaa@ana.com", 
    name="aaana",
    avatar_url="anaaaaa",
    password_hash="12345a11"
)

# routes

@router.post("/login")
def login():
    pass


@router.post("/signup")
def signup(user_create: UserCreate, db = Depends(get_db)):
    # here we already know that the data is valid for the table
    
    existing_user = db.query(UserRecord).filter(UserRecord.email == user_create.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    password_hash = bcrypt.hashpw(user_create.password_hash.encode(), bcrypt.gensalt())
    
    new_user = UserRecord( 
        email=user_create.email,
        name=user_create.name,
        avatar_url=user_create.avatar_url,
        password_hash=password_hash
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # from UserRecord to User(pydantic):
    # transform and validate
    user = User.model_validate(new_user)
    
    access_token =  create_access_token(user.id) 
    
    # return user # pydantic obj are transformable to json
    return TokenResponse(
        user=user,
        access_token=access_token)