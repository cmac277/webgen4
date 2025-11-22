# server.py
from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from bson import ObjectId
import os
import shutil
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "flooring_business")

# FastAPI app
app = FastAPI(
    title="Professional Flooring Business API",
    description="Backend API for a professional flooring business website",
    version="1.0.0"
)

# Create directories for static files
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Create default images directory
DEFAULT_IMAGES_DIR = Path("static/images")
DEFAULT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB client
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

# Collections
services_collection = db.services
projects_collection = db.projects
quotes_collection = db.quotes
testimonials_collection = db.testimonials
contact_collection = db.contact_messages
landing_content_collection = db.landing_content

# Helper function for ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Pydantic Models
class ServiceModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    price_range: str
    image_url: Optional[str] = None
    features: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ProjectModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: str
    service_type: str
    location: str
    area_size: str
    image_urls: List[str] = []
    completion_date: date
    is_featured: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, date: str}

class QuoteRequestModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: str
    city: str
    zip_code: str
    service_type: str
    project_description: str
    preferred_contact_method: str
    area_size: Optional[str] = None
    timeline: Optional[str] = None
    budget_range: Optional[str] = None
    status: str = "pending"  # pending, contacted, quoted, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TestimonialModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    customer_name: str
    location: str
    rating: int = Field(..., ge=1, le=5)
    review_text: str
    service_type: str
    project_date: date
    is_featured: bool = False
    is_approved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, date: str}

class ContactMessageModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: str
    message: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Landing Page Models
class HeroSectionModel(BaseModel):
    title: str
    subtitle: str
    description: str
    background_image: str
    cta_primary_text: str
    cta_primary_link: str
    cta_secondary_text: str
    cta_secondary_link: str

class FeatureModel(BaseModel):
    icon: str
    title: str
    description: str

class StatisticModel(BaseModel):
    value: str
    label: str
    description: str

class LandingPageModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    hero_section: HeroSectionModel
    features: List[FeatureModel]
    statistics: List[StatisticModel]
    about_summary: str
    why_choose_us: List[str]
    service_areas_summary: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Company Info Model (for About Us page)
class CompanyInfoModel(BaseModel):
    company_name: str = "Premium Flooring Solutions"
    tagline: str = "Quality Flooring, Exceptional Service"
    about_description: str
    years_experience: int
    phone: str
    email: EmailStr
    address: str
    business_hours: dict
    service_areas: List[str]
    certifications: List[str] = []
    social_media: dict = {}

# File Upload Model
class ImageUploadResponse(BaseModel):
    filename: str
    url: str
    size: int

# Routes

@app.get("/")
async def root():
    return {"message": "Professional Flooring Business API", "version": "1.0.0"}

# Image Upload Routes
@app.post("/api/upload/image", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = file_path.stat().st_size
    
    return ImageUploadResponse(
        filename=unique_filename,
        url=f"/static/uploads/{unique_filename}",
        size=file_size
    )

# Landing Page Routes
@app.get("/api/landing-page", response_model=LandingPageModel)
async def get_landing_page():
    landing_page = await landing_content_collection.find_one({})
    
    if not landing_page:
        # Return default landing page content
        default_content = LandingPageModel(
            hero_section=HeroSectionModel(
                title="Premium Flooring Solutions",
                subtitle="Transform Your Space with Expert Flooring",
                description="Professional hardwood, laminate, tile, and carpet installation services with over 15 years of experience. Quality craftsmanship, competitive pricing, and customer satisfaction guaranteed.",
                background_image="/static/images/hero-background.jpg",
                cta_primary_text="Get Free Quote",
                cta_primary_link="#quote",
                cta_secondary_text="View Our Work",
                cta_secondary_link="#portfolio"
            ),
            features=[
                FeatureModel(
                    icon="🏠",
                    title="Expert Installation",
                    description="Professional installation by certified craftsmen with attention to detail"
                ),
                FeatureModel(
                    icon="💰",
                    title="Competitive Pricing",
                    description="Fair, transparent pricing with free estimates and no hidden fees"
                ),
                FeatureModel(
                    icon="🛡️",
                    title="Quality Guaranteed",
                    description="Fully insured and bonded with warranty on all work performed"
                ),
                FeatureModel(
                    icon="⏰",
                    title="Timely Service",
                    description="On-time project completion with flexible scheduling options"
                )
            ],
            statistics=[
                StatisticModel(
                    value="500+",
                    label="Projects Completed",
                    description="Satisfied customers across the region"
                ),
                StatisticModel(
                    value="15+",
                    label="Years Experience",
                    description="Trusted expertise in flooring solutions"
                ),
                StatisticModel(
                    value="98%",
                    label="Customer Satisfaction",
                    description="Excellence in service and quality"
                ),
                StatisticModel(
                    value="24/7",
                    label="Support Available",
                    description="We're here when you need us"
                )
            ],
            about_summary="Premium Flooring Solutions has been the trusted choice for residential and commercial flooring needs for over 15 years. Our expert team specializes in hardwood, laminate, tile, vinyl, and carpet installation with a commitment to quality craftsmanship and customer satisfaction.",
            why_choose_us=[
                "Licensed, bonded, and insured professionals",
                "Free in-home consultations and estimates",
                "Wide selection of premium flooring materials",
                "Competitive pricing with flexible payment options",
                "Complete project management from start to finish",
                "Satisfaction guarantee on all work"
            ],
            service_areas_summary="Proudly serving the greater metropolitan area including Downtown, Suburbs, North District, and South Valley. Contact us to confirm service availability in your location."
        )
        return default_content
    
    return landing_page

@app.post("/api/landing-page", response_model=LandingPageModel)
async def update_landing_page(landing_page: LandingPageModel):
    landing_dict = landing_page.dict(by_alias=True, exclude_unset=True)
    if "_id" in landing_dict:
        del landing_dict["_id"]
    
    # Upsert landing page content
    await landing_content_collection.replace_one({}, landing_dict, upsert=True)
    updated_page = await landing_content_collection.find_one({})
    return updated_page

# Default Sample Data Routes
@app.post("/api/initialize/sample-data")
async def initialize_sample_data():
    """Initialize the database with sample data for demonstration"""
    
    # Sample Services
    sample_services = [
        {
            "name": "Hardwood Flooring",
            "description": "Premium hardwood installation including oak, maple, cherry, and exotic woods",
            "price_range": "$8-15 per sq ft",
            "image_url": "/static/images/hardwood-flooring.jpg",
            "features": ["Solid wood options", "Engineered hardwood", "Custom staining", "Refinishing services"],
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "name": "Luxury Vinyl Plank",
            "description": "Waterproof luxury vinyl plank flooring perfect for any room",
            "price_range": "$4-8 per sq ft",
            "image_url": "/static/images/luxury-vinyl.jpg",
            "features": ["100% waterproof", "Realistic wood look", "Easy maintenance", "Scratch resistant"],
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "name": "Ceramic & Porcelain Tile",
            "description": "Elegant tile installation for kitchens, bathrooms, and living spaces",
            "price_range": "$6-12 per sq ft",
            "image_url": "/static/images/ceramic-tile.jpg",
            "features": ["Water resistant", "Easy to clean", "Variety of designs", "Long lasting"],
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "name": "Carpet Installation",
            "description": "Comfortable carpet installation with premium padding",
            "price_range": "$3-8 per sq ft",
            "image_url": "/static/images/carpet.jpg",
            "features": ["Various textures", "Stain protection", "Sound dampening", "Warm and cozy"],
            "is_active": True,
            "created_at": datetime.utcnow()
        }
    ]
    
    await services_collection.delete_many({})
    await services_collection.insert_many(sample_services)
    
    # Sample Projects
    sample_projects = [
        {
            "title": "Modern Kitchen Hardwood Installation",
            "description": "Complete kitchen renovation with premium oak hardwood flooring",
            "service_type": "Hardwood Flooring",
            "location": "Downtown District",
            "area_size": "400 sq ft",
            "image_urls": ["/static/images/project-kitchen-1.jpg", "/static/images/project-kitchen-2.jpg"],
            "completion_date": date(2024, 1, 15),
            "is_featured": True,
            "created_at": datetime.utcnow()
        },
        {
            "title": "Bathroom Tile Renovation",
            "description": "Luxury bathroom with ceramic tile flooring and accent walls",
            "service_type": "Ceramic & Porcelain Tile",
            "location": "Suburbs",
            "area_size": "80 sq ft",
            "image_urls": ["/static/images/project-bathroom-1.jpg"],
            "completion_date": date(2024, 2, 1),
            "is_featured": True,
            "created_at": datetime.utcnow()
        },
        {
            "title": "Living Room Luxury Vinyl",
            "description": "Open concept living room with waterproof luxury vinyl plank",
            "service_type": "Luxury Vinyl Plank",
            "location": "North District",
            "area_size": "600 sq ft",
            "image_urls": ["/static/images/project-living-1.jpg"],
            "completion_date":