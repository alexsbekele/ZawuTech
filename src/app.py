from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.schemas import UserRegister, UserLogin, Post
from src.database import get_db
from src import models
import shutil
import os

router = APIRouter()

# --- Config ---
SECRET_KEY = "makethisverylongandrandom123!"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30
UPLOAD_DIR = "Template/static/uploads"

# --- Helpers ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    data = {"sub": username, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# --- Auth Routes ---
@router.post("/register/")
async def register_user(user: UserRegister, db: Session = Depends(get_db)):
    # Check if username exists in database
    existing = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Create new user object
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": f"User '{user.username}' registered successfully"}

@router.post("/login/")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    # Find user in database
    db_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_token(db_user.username)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me/")
async def get_me(current_user: str = Depends(get_current_user)):
    return {"logged_in_as": current_user}

# --- Post Routes ---
@router.post("/posts/")
async def create_post(
    post: Post,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find the user in database
    db_user = db.query(models.User).filter(
        models.User.username == current_user
    ).first()

    # Create new post object
    new_post = models.Post(
        title=post.title,
        content=post.content,
        image_url=post.image_url,
        author=current_user,
        owner_id=db_user.id
    )

    # Save to database
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.get("/posts/")
async def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

# --- Upload Route ---
@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {
        "uploaded_by": current_user,
        "filename": file.filename,
        "url": f"/static/uploads/{file.filename}"
    }