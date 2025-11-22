# server.py
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from bson import ObjectId
import os
import aiofiles
import uuid
from pathlib import Path
import mimetypes

# Create directories for file storage
Path("uploads/videos").mkdir(parents=True, exist_ok=True)
Path("uploads/thumbnails").mkdir(parents=True, exist_ok=True)
Path("uploads/avatars").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="YouTube Clone API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "youtube_clone"

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    avatar_url: Optional[str] = None
    subscriber_count: int = 0
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    tags: List[str] = []
    category: Optional[str] = None

class VideoCreate(VideoBase):
    pass

class VideoResponse(VideoBase):
    id: str
    uploader_id: str
    uploader_name: str
    video_url: str
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    views: int = 0
    likes: int = 0
    dislikes: int = 0
    upload_date: datetime

class CommentCreate(BaseModel):
    content: str
    video_id: str

class CommentResponse(BaseModel):
    id: str
    content: str
    user_id: str
    user_name: str
    video_id: str
    likes: int = 0
    created_at: datetime

class PlaylistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = True

class PlaylistResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    creator_id: str
    creator_name: str
    video_count: int = 0
    is_public: bool = True
    created_at: datetime

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends()):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return user

def convert_object_id(doc):
    """Convert MongoDB ObjectId to string"""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

# Authentication routes
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = await db.users.find_one({"username": user.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_doc = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "password": hashed_password,
        "avatar_url": None,
        "subscriber_count": 0,
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    return UserResponse(**convert_object_id(user_doc))

@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User routes
@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(**convert_object_id(current_user))

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**convert_object_id(user))
    except:
        raise HTTPException(status_code=404, detail="User not found")

# Video routes
@app.post("/api/videos/upload")
async def upload_video(
    title: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
    category: str = Form(""),
    video: UploadFile = File(...),
    thumbnail: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    # Validate video file
    if not video.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid video file")
    
    # Generate unique filename
    video_id = str(uuid.uuid4())
    video_ext = os.path.splitext(video.filename)[1]
    video_filename = f"{video_id}{video_ext}"
    video_path = f"uploads/videos/{video_filename}"
    
    # Save video file
    async with aiofiles.open(video_path, 'wb') as f:
        content = await video.read()
        await f.write(content)
    
    # Handle thumbnail
    thumbnail_url = None
    if thumbnail:
        thumbnail_ext = os.path.splitext(thumbnail.filename)[1]
        thumbnail_filename = f"{video_id}_thumb{thumbnail_ext}"
        thumbnail_path = f"uploads/thumbnails/{thumbnail_filename}"
        
        async with aiofiles.open(thumbnail_path, 'wb') as f:
            thumb_content = await thumbnail.read()
            await f.write(thumb_content)
        
        thumbnail_url = f"/uploads/thumbnails/{thumbnail_filename}"
    
    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
    
    # Create video document
    video_doc = {
        "title": title,
        "description": description,
        "tags": tag_list,
        "category": category,
        "uploader_id": str(current_user["_id"]),
        "uploader_name": current_user["username"],
        "video_url": f"/uploads/videos/{video_filename}",
        "thumbnail_url": thumbnail_url,
        "duration": None,  # Would need video processing to get duration
        "views": 0,
        "likes": 0,
        "dislikes": 0,
        "upload_date": datetime.utcnow()
    }
    
    result = await db.videos.insert_one(video_doc)
    video_doc["_id"] = result.inserted_id
    
    return {"message": "Video uploaded successfully", "video_id": str(result.inserted_id)}

@app.get("/api/videos", response_model=List[VideoResponse])
async def get_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    query = {}
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}}
        ]
    
    if category:
        query["category"] = category
    
    cursor = db.videos.find(query).sort("upload_date", -1).skip(skip).limit(limit)
    videos = await cursor.to_list(length=None)
    
    return [VideoResponse(**convert_object_id(video)) for video in videos]

@app.get("/api/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str):
    try:
        video = await db.videos.find_one({"_id": ObjectId(video_id)})
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Increment view count
        await db.videos.update_one(
            {"_id": ObjectId(video_id)},
            {"$inc": {"views": 1}}
        )
        video["views"] += 1
        
        return VideoResponse(**convert_object_id(video))
    except:
        raise HTTPException(status_code=404, detail="Video not found")

@app.post("/api/videos/{video_id}/like")
async def like_video(video_id: str, current_user: dict = Depends(get_current_user)):
    try:
        # Check if user already liked this video
        existing_like = await db.likes.find_one({
            "user_id": str(current_user["_id"]),
            "video_id": video_id,
            "type": "like"
        })
        
        if existing_like:
            # Remove like
            await db.likes.delete_one({"_id": existing_like["_id"]})
            await db.videos.update_one(
                {"_id": ObjectId(video_id)},
                {"$inc": {"likes": -1}}
            )
            return {"message": "Like removed"}
        else:
            # Remove dislike if exists
            await db.likes.delete_one({
                "user_id": str(current_user["_id"]),
                "video_id": video_id,
                "type": "dislike"
            })
            
            # Add like
            await db.likes.insert_one({
                "user_id": str(current_user["_id"]),
                "video_id": video_id,
                "type": "like",
                "created_at": datetime.utcnow()
            })
            
            # Update video likes count
            await db.videos.update_one(
                {"_id": ObjectId(video_id)},
                {"$inc": {"likes": 1, "dislikes": 0}}  # Remove dislike if it existed
            )
            
            return {"message": "Video liked"}
    except:
        raise HTTPException(status_code=404, detail="Video not found")

@app.post("/api/videos/{video_id}/dislike")
async def dislike_video(video_id: str, current_user: dict = Depends(get_current_user)):
    try:
        # Check if user already disliked this video
        existing_dislike = await db.likes.find_one({
            "user_id": str(current_user["_id"]),
            "video_id": video_id,
            "type": "dislike"
        })
        
        if existing_dislike:
            # Remove dislike
            await db.likes.delete_one({"_id": existing_dislike["_id"]})
            await db.videos.update_one(
                {"_id": ObjectId(video_id)},
                {"$inc": {"dislikes": -1}}
            )
            return {"message": "Dislike removed"}
        else:
            # Remove like if exists
            await db.likes.delete_one({
                "user_id": str(current_user["_id"]),
                "video_id": video_id,
                "type": "like"
            })
            
            # Add dislike
            await db.likes.insert_one({
                "user_id": str(current_user["_id"]),
                "video_id": video_id,
                "type": "dislike",
                "created_at": datetime.utcnow()
            })
            
            # Update video dislikes count
            await db.videos.update_one(
                {"_id": ObjectId(video_id)},
                {"$inc": {"dislikes": 1, "likes": 0}}  # Remove like if it existed
            )
            
            return {"message": "Video disliked"}
    except:
        raise HTTPException(status_code=404, detail="Video not found")

# Comment routes
@app.post("/api/comments", response_model=CommentResponse)
async def create_comment(comment: CommentCreate, current_user: dict = Depends(get_current_user)):
    comment_doc = {
        "content": comment.content,
        "user_id": str(current_user["_id"]),
        "user_name": current_user["username"],
        "video_id": comment.video_id,
        "likes": 0,
        "created_at": datetime.utcnow()