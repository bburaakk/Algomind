# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from . import database, models, jwt

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CORS - Kivy erişebilsin diye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    email: str
    password: str
    role: str  # frontend'de dropdown olabilir

@app.post("/signup", status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, password=hashed, role=user.role)
    db.add(db_user)
    db.commit()
    return {"msg": "User created"}

class LoginData(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(user: LoginData, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.create_access_token({"sub": db_user.email, "role": db_user.role})
    return {"access_token": token, "token_type": "bearer"}
