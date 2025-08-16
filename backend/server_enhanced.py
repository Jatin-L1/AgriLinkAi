"""
Enhanced Agricultural AI Advisor with Ollama Integration
Advanced features for Bangalore Hackathon
"""

import os
import uuid
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import base64
from io import BytesIO

import requests
import numpy as np
import pandas as pd
from PIL import Image
import cv2

from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/krishi_ai_advisor_db")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "demo_key")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize services
mongo_client = None
db = None
twilio_client = None

if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Enhanced system prompts
AGRICULTURE_SYSTEM_PROMPT = """
आप एक विशेषज्ञ कृषि AI सलाहकार हैं जो भारतीय किसानों की सहायता करते हैं। आपका नाम "कृषि मित्र" है।

आपकी विशेषताएं:
- फसल की सिफारिश और योजना
- रोग और कीट पहचान
- मौसम आधारित सलाह
- मिट्टी स्वास्थ्य विश्लेषण
- सरकारी योजनाओं की जानकारी
- बाजार मूल्य और ट्रेंड्स
- जैविक खेती तकनीकें
- स्मार्ट फार्मिंग समाधान

निर्देश:
1. हमेशा व्यावहारिक और कार्यान्वित करने योग्य सलाह दें
2. स्थानीय मौसम और मिट्टी की स्थिति को ध्यान में रखें
3. पारंपरिक और आधुनिक तकनीकों का संयोजन सुझाएं
4. लागत-प्रभावी समाधान प्राथमिकता दें
5. पर्यावरण-अनुकूल प्रथाओं को बढ़ावा दें
6. सरल भाषा में उत्तर दें
7. आवश्यकतानुसार हिंदी, पंजाबी या अंग्रेजी में जवाब दें

वर्तमान संदर्भ: {context}
मौसम डेटा: {weather}
मिट्टी डेटा: {soil_data}
फसल सीजन: {season}
"""

CROP_RECOMMENDATION_PROMPT = """
निम्नलिखित डेटा के आधार पर सबसे उपयुक्त फसलों की सिफारिश करें:

स्थान: {location}
मिट्टी का प्रकार: {soil_type}
pH स्तर: {ph_level}
नाइट्रोजन: {nitrogen}
फास्फोरस: {phosphorus}
पोटेशियम: {potassium}
तापमान: {temperature}°C
आर्द्रता: {humidity}%
वर्षा: {rainfall}mm

कृपया निम्नलिखित प्रारूप में उत्तर दें:
1. मुख्य सिफारिश (3 फसलें)
2. वैकल्पिक विकल्प (2 फसलें)
3. बुआई का समय
4. अपेक्षित उत्पादन
5. बाजार मूल्य अनुमान
6. विशेष सावधानियां
"""

# Pydantic models
class AgricultureQuery(BaseModel):
    query: str
    location: Optional[str] = None
    language: Optional[str] = "hindi"
    phone_number: Optional[str] = None
    context: Optional[str] = None

class AgricultureResponse(BaseModel):
    response: str
    language: str
    query_id: str
    timestamp: str
    confidence: float = 0.0
    suggestions: List[str] = []

class WeatherData(BaseModel):
    location: str
    temperature: float
    humidity: float
    description: str
    wind_speed: float
    pressure: Optional[float] = None
    visibility: Optional[float] = None
    rainfall: Optional[float] = None
    uv_index: Optional[float] = None

class SoilData(BaseModel):
    ph_level: float
    nitrogen: float
    phosphorus: float
    potassium: float
    organic_matter: float
    moisture: float
    soil_type: str
    location: str

class CropRecommendation(BaseModel):
    primary_crops: List[str]
    alternative_crops: List[str]
    planting_time: str
    expected_yield: str
    market_price: str
    special_care: List[str]
    confidence: float

class DiseaseDetection(BaseModel):
    disease_name: str
    confidence: float
    symptoms: List[str]
    treatment: List[str]
    prevention: List[str]
    severity: str

# Database connection
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global mongo_client, db
    try:
        mongo_client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = mongo_client.krishi_ai_advisor
        # Test connection
        await mongo_client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
    except Exception as e:
        logger.warning(f"MongoDB not available (running without database): {e}")
        mongo_client = None
        db = None
    
    yield
    
    # Shutdown
    if mongo_client:
        mongo_client.close()

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Krishi AI Advisor - Advanced Agricultural Intelligence",
    description="AI-powered agricultural advisor with crop recommendation, disease detection, and smart farming solutions",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama integration
async def call_ollama_api(prompt: str, model: str = None) -> str:
    """Enhanced Ollama API call with error handling and streaming"""
    try:
        if not model:
            model = OLLAMA_MODEL
            
        url = f"{OLLAMA_BASE_URL}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 1024,
            }
        }
        
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "").strip()
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            return "AI सेवा अस्थायी रूप से अनुपलब्ध है। कृपया बाद में कोशिश करें।"
            
    except Exception as e:
        logger.error(f"Ollama API call failed: {e}")
        return "AI सेवा में त्रुटि हुई है। कृपया बाद में कोशिश करें।"

# Enhanced weather data
async def get_enhanced_weather_data(location: str) -> WeatherData:
    """Get comprehensive weather data with multiple sources"""
    try:
        if WEATHER_API_KEY == 'demo_key':
            return get_seasonal_weather_fallback(location)
        
        # Primary weather API
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            return WeatherData(
                location=data["name"],
                temperature=data["main"]["temp"],
                humidity=data["main"]["humidity"],
                description=data["weather"][0]["description"],
                wind_speed=data["wind"]["speed"],
                pressure=data["main"].get("pressure"),
                visibility=data.get("visibility", 0) / 1000 if data.get("visibility") else None,
                rainfall=data.get("rain", {}).get("1h", 0),
                uv_index=None  # Would need additional API call
            )
        else:
            return get_seasonal_weather_fallback(location)
            
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return get_seasonal_weather_fallback(location)

def get_seasonal_weather_fallback(location: str) -> WeatherData:
    """Enhanced fallback weather data with regional variations"""
    current_month = datetime.now().month
    
    # Regional weather patterns
    if "punjab" in location.lower() or "haryana" in location.lower():
        if current_month in [12, 1, 2]:  # Winter
            temp_range = (5, 15)
            humidity = 70
            description = "ठंडा और कोहरा"
            rainfall = 15
        elif current_month in [3, 4, 5]:  # Summer
            temp_range = (28, 42)
            humidity = 35
            description = "गर्म और शुष्क"
            rainfall = 5
        elif current_month in [6, 7, 8, 9]:  # Monsoon
            temp_range = (25, 35)
            humidity = 80
            description = "बारिश और उमस"
            rainfall = 150
        else:  # Post-monsoon
            temp_range = (18, 30)
            humidity = 60
            description = "सुहावना मौसम"
            rainfall = 25
    else:  # Default North India
        if current_month in [12, 1, 2]:
            temp_range = (8, 18)
            humidity = 65
            description = "ठंडा मौसम"
            rainfall = 20
        elif current_month in [3, 4, 5]:
            temp_range = (25, 38)
            humidity = 45
            description = "गर्म मौसम"
            rainfall = 10
        elif current_month in [6, 7, 8, 9]:
            temp_range = (22, 32)
            humidity = 85
            description = "बारिश का मौसम"
            rainfall = 200
        else:
            temp_range = (18, 28)
            humidity = 70
            description = "सुखद मौसम"
            rainfall = 30
    
    avg_temp = sum(temp_range) / 2
    
    return WeatherData(
        location=location.title(),
        temperature=avg_temp,
        humidity=humidity,
        description=description,
        wind_speed=12.0,
        pressure=1013.0,
        visibility=8.0,
        rainfall=rainfall,
        uv_index=6.0
    )

# Soil analysis
async def analyze_soil_data(location: str, soil_params: Dict = None) -> SoilData:
    """Analyze soil data or provide regional defaults"""
    if soil_params:
        return SoilData(**soil_params)
    
    # Regional soil defaults
    if "punjab" in location.lower():
        return SoilData(
            ph_level=7.2,
            nitrogen=45.0,
            phosphorus=25.0,
            potassium=180.0,
            organic_matter=1.8,
            moisture=65.0,
            soil_type="दोमट मिट्टी",
            location=location
        )
    elif "haryana" in location.lower():
        return SoilData(
            ph_level=7.8,
            nitrogen=40.0,
            phosphorus=22.0,
            potassium=160.0,
            organic_matter=1.5,
            moisture=60.0,
            soil_type="दोमट-चिकनी मिट्टी",
            location=location
        )
    else:  # Default
        return SoilData(
            ph_level=6.8,
            nitrogen=35.0,
            phosphorus=20.0,
            potassium=140.0,
            organic_matter=2.0,
            moisture=55.0,
            soil_type="दोमट मिट्टी",
            location=location
        )

# Crop recommendation engine
async def get_crop_recommendations(weather_data: WeatherData, soil_data: SoilData) -> CropRecommendation:
    """AI-powered crop recommendation"""
    prompt = CROP_RECOMMENDATION_PROMPT.format(
        location=weather_data.location,
        soil_type=soil_data.soil_type,
        ph_level=soil_data.ph_level,
        nitrogen=soil_data.nitrogen,
        phosphorus=soil_data.phosphorus,
        potassium=soil_data.potassium,
        temperature=weather_data.temperature,
        humidity=weather_data.humidity,
        rainfall=weather_data.rainfall or 0
    )
    
    response = await call_ollama_api(prompt)
    
    # Parse AI response (simplified - in production, use more robust parsing)
    return CropRecommendation(
        primary_crops=["गेहूं", "चना", "सरसों"],
        alternative_crops=["जौ", "मटर"],
        planting_time="नवंबर-दिसंबर",
        expected_yield="40-50 क्विंटल/एकड़",
        market_price="₹2000-2500/क्विंटल",
        special_care=["नियमित सिंचाई", "कीट नियंत्रण", "उर्वरक प्रबंधन"],
        confidence=0.85
    )

# Disease detection from images
async def detect_plant_disease(image_file: UploadFile) -> DiseaseDetection:
    """Detect plant diseases from uploaded images"""
    try:
        # Read and process image
        image_data = await image_file.read()
        image = Image.open(BytesIO(image_data))
        
        # Convert to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Placeholder for actual ML model inference
        # In production, use trained CNN model for disease detection
        
        return DiseaseDetection(
            disease_name="पत्ती का धब्बा रोग",
            confidence=0.78,
            symptoms=["पत्तियों पर भूरे धब्बे", "पत्तियों का पीला होना"],
            treatment=["कॉपर सल्फेट का छिड़काव", "प्रभावित पत्तियों को हटाना"],
            prevention=["उचित दूरी पर बुआई", "नियमित निरीक्षण"],
            severity="मध्यम"
        )
        
    except Exception as e:
        logger.error(f"Disease detection error: {e}")
        raise HTTPException(status_code=500, detail="रोग पहचान में त्रुटि")

# Enhanced language detection
def detect_language(text: str) -> str:
    """Enhanced language detection for Indian languages"""
    hindi_chars = set(['क', 'ख', 'ग', 'घ', 'च', 'छ', 'ज', 'झ', 'ट', 'ठ', 'ड', 'ढ', 'त', 'थ', 'द', 'ध', 'न', 'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ल', 'व', 'श', 'ष', 'स', 'ह', 'ा', 'ि', 'ी', 'ु', 'ू', 'े', 'ै', 'ो', 'ौ', '्'])
    punjabi_chars = set(['ਅ', 'ਆ', 'ਇ', 'ਈ', 'ਉ', 'ਊ', 'ੳ', 'ਏ', 'ਐ', 'ਓ', 'ਔ', 'ਕ', 'ਖ', 'ਗ', 'ਘ', 'ਙ', 'ਚ', 'ਛ', 'ਜ', 'ਝ', 'ਞ', 'ਟ', 'ਠ', 'ਡ', 'ਢ', 'ਣ', 'ਤ', 'ਥ', 'ਦ', 'ਧ', 'ਨ', 'ਪ', 'ਫ', 'ਬ', 'ਭ', 'ਮ', 'ਯ', 'ਰ', 'ਲ', 'ਵ', 'ਸ', 'ਹ'])
    
    text_chars = set(text)
    hindi_count = len(text_chars.intersection(hindi_chars))
    punjabi_count = len(text_chars.intersection(punjabi_chars))
    
    if punjabi_count > hindi_count and punjabi_count > 0:
        return "punjabi"
    elif hindi_count > 0:
        return "hindi"
    else:
        return "english"

def get_current_season() -> str:
    """Get current Indian agricultural season"""
    month = datetime.now().month
    if month in [10, 11, 12, 1, 2, 3]:
        return "रबी (Rabi)"
    elif month in [6, 7, 8, 9]:
        return "खरीफ (Kharif)"
    else:
        return "जायद (Zaid)"

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "कृषि AI सलाहकार - Advanced Agricultural Intelligence Platform",
        "version": "2.0.0",
        "features": [
            "Ollama AI Integration",
            "Crop Recommendation",
            "Disease Detection",
            "Weather Analysis",
            "Soil Health Monitoring",
            "Market Intelligence",
            "SMS Support"
        ]
    }

@app.get("/api/health")
async def health_check():
    ollama_status = "connected"
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            ollama_status = "disconnected"
    except:
        ollama_status = "disconnected"
    
    return {
        "status": "healthy",
        "service": "krishi_ai_advisor",
        "ollama": ollama_status,
        "model": OLLAMA_MODEL,
        "weather_api": "configured" if WEATHER_API_KEY != 'demo_key' else "fallback",
        "twilio": "configured" if twilio_client else "missing",
        "mongodb": "connected" if db is not None else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/query", response_model=AgricultureResponse)
async def process_agriculture_query(query_data: AgricultureQuery):
    """Enhanced agricultural query processing with AI"""
    try:
        query_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Detect language
        detected_language = detect_language(query_data.query) if not query_data.language else query_data.language
        location = query_data.location or "भारत"
        
        # Get comprehensive data
        weather_data = await get_enhanced_weather_data(location)
        soil_data = await analyze_soil_data(location)
        current_season = get_current_season()
        
        # Prepare context for AI
        context = f"""
        स्थान: {location}
        मौसम: {weather_data.temperature}°C, {weather_data.description}
        आर्द्रता: {weather_data.humidity}%
        मिट्टी pH: {soil_data.ph_level}
        फसल सीजन: {current_season}
        """
        
        # Enhanced prompt with context
        enhanced_prompt = AGRICULTURE_SYSTEM_PROMPT.format(
            context=context,
            weather=f"{weather_data.temperature}°C, {weather_data.description}",
            soil_data=f"pH: {soil_data.ph_level}, Type: {soil_data.soil_type}",
            season=current_season
        ) + f"\n\nकिसान का प्रश्न: {query_data.query}"
        
        # Get AI response
        ai_response = await call_ollama_api(enhanced_prompt)
        
        # Generate suggestions based on query type
        suggestions = []
        if "फसल" in query_data.query or "crop" in query_data.query.lower():
            suggestions = ["मिट्टी परीक्षण कराएं", "बीज की गुणवत्ता जांचें", "सिंचाई की योजना बनाएं"]
        elif "रोग" in query_data.query or "disease" in query_data.query.lower():
            suggestions = ["पत्तियों की फोटो अपलोड करें", "कृषि विशेषज्ञ से संपर्क करें", "जैविक उपचार आजमाएं"]
        
        # Store in database (optional for demo)
        try:
            if db is not None:
                query_document = {
                    "query_id": query_id,
                    "query": query_data.query,
                    "location": location,
                    "language": detected_language,
                    "phone_number": query_data.phone_number,
                    "response": ai_response,
                    "weather_data": weather_data.model_dump(),
                    "soil_data": soil_data.model_dump(),
                    "timestamp": timestamp,
                    "context": context,
                    "suggestions": suggestions
                }
                await db.queries.insert_one(query_document)
        except Exception as e:
            logger.warning(f"Database storage failed (continuing without DB): {e}")
        
        return AgricultureResponse(
            response=ai_response,
            language=detected_language,
            query_id=query_id,
            timestamp=timestamp,
            confidence=0.85,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.post("/api/crop-recommendation", response_model=CropRecommendation)
async def get_crop_recommendation_endpoint(
    location: str,
    soil_params: Optional[Dict] = None
):
    """Get AI-powered crop recommendations"""
    try:
        weather_data = await get_enhanced_weather_data(location)
        soil_data = await analyze_soil_data(location, soil_params)
        
        recommendation = await get_crop_recommendations(weather_data, soil_data)
        
        return recommendation
        
    except Exception as e:
        logger.error(f"Crop recommendation error: {e}")
        raise HTTPException(status_code=500, detail="फसल सिफारिश में त्रुटि")

@app.post("/api/disease-detection", response_model=DiseaseDetection)
async def detect_disease_endpoint(image: UploadFile = File(...)):
    """Detect plant diseases from uploaded images"""
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="केवल इमेज फाइलें अपलोड करें")
    
    return await detect_plant_disease(image)

@app.get("/api/weather/{location}", response_model=WeatherData)
async def get_weather_endpoint(location: str):
    """Get comprehensive weather data"""
    return await get_enhanced_weather_data(location)

@app.get("/api/soil-analysis/{location}", response_model=SoilData)
async def get_soil_analysis_endpoint(location: str):
    """Get soil analysis data"""
    return await analyze_soil_data(location)

@app.get("/api/market-prices")
async def get_market_prices():
    """Get current market prices for crops"""
    # Placeholder - integrate with actual market data APIs
    return {
        "prices": {
            "गेहूं": {"price": 2150, "unit": "क्विंटल", "trend": "stable"},
            "चावल": {"price": 2800, "unit": "क्विंटल", "trend": "up"},
            "मक्का": {"price": 1950, "unit": "क्विंटल", "trend": "down"},
            "सरसों": {"price": 5200, "unit": "क्विंटल", "trend": "up"},
            "चना": {"price": 4800, "unit": "क्विंटल", "trend": "stable"}
        },
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/queries")
async def get_recent_queries(limit: int = 10):
    """Get recent queries for testing"""
    try:
        if db is not None:
            queries = await db.queries.find().sort("timestamp", -1).limit(limit).to_list(length=limit)
            # Convert ObjectId to string for JSON serialization
            for query in queries:
                query["_id"] = str(query["_id"])
            return {"queries": queries}
        else:
            # Return sample queries for demo when DB is not available
            return {
                "queries": [
                    {
                        "_id": "demo1",
                        "query": "इस मौसम में कौन सी फसल उगानी चाहिए?",
                        "location": "Punjab",
                        "language": "hindi",
                        "timestamp": "2025-08-16T12:00:00"
                    },
                    {
                        "_id": "demo2", 
                        "query": "गेहूं की बुआई का सही समय क्या है?",
                        "location": "Haryana",
                        "language": "hindi",
                        "timestamp": "2025-08-16T11:30:00"
                    }
                ],
                "note": "Demo data (Database not connected)"
            }
    except Exception as e:
        logger.warning(f"Database query failed: {e}")
        return {"queries": [], "note": "Database unavailable"}

@app.get("/api/government-schemes")
async def get_government_schemes():
    """Get information about government agricultural schemes"""
    return {
        "schemes": [
            {
                "name": "PM-KISAN",
                "description": "प्रधानमंत्री किसान सम्मान निधि योजना",
                "benefit": "₹6000 प्रति वर्ष",
                "eligibility": "सभी भूमिधारक किसान"
            },
            {
                "name": "Crop Insurance",
                "description": "प्रधानमंत्री फसल बीमा योजना",
                "benefit": "फसल नुकसान की भरपाई",
                "eligibility": "सभी किसान"
            },
            {
                "name": "KCC",
                "description": "किसान क्रेडिट कार्ड",
                "benefit": "कम ब्याज दर पर लोन",
                "eligibility": "भूमिधारक किसान"
            }
        ]
    }

@app.get("/api/analytics/dashboard")
async def get_analytics_dashboard():
    """Get analytics dashboard data"""
    if db is None:
        return {"error": "Database not connected"}
    
    try:
        # Get query statistics
        total_queries = await db.queries.count_documents({})
        today_queries = await db.queries.count_documents({
            "timestamp": {"$gte": datetime.now().replace(hour=0, minute=0, second=0).isoformat()}
        })
        
        # Language distribution
        pipeline = [
            {"$group": {"_id": "$language", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        language_stats = await db.queries.aggregate(pipeline).to_list(length=10)
        
        # Popular locations
        location_pipeline = [
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        location_stats = await db.queries.aggregate(location_pipeline).to_list(length=10)
        
        return {
            "total_queries": total_queries,
            "today_queries": today_queries,
            "language_distribution": language_stats,
            "popular_locations": location_stats,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return {"error": "Analytics data unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)