# main.py

# --- 1. ALL IMPORTS AT THE TOP ---
import re
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from urllib.parse import urlparse
from passlib.context import CryptContext
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from fastapi.staticfiles import StaticFiles

# Local imports (must not be relative)
import models
import database
from database import SessionLocal, engine

# --- 2. INITIAL SETUP ---

# Create the FastAPI app instance
app = FastAPI()

# Setup for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 3. MIDDLEWARE (Order is important) ---

# Secret key for signing session cookies
app.add_middleware(SessionMiddleware, secret_key="!replace_this_with_a_real_secret_key!")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# This line tells FastAPI to serve all files from the 'static' folder
# when a URL starts with '/static'
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- 4. DATABASE DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 5. GOOGLE OAUTH SETUP ---
config = Config()
oauth = OAuth(config)

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id='YOUR_GOOGLE_CLIENT_ID',       # Paste your Client ID here
    client_secret='YOUR_GOOGLE_CLIENT_SECRET', # Paste your Client Secret here
    client_kwargs={'scope': 'openid email profile'}
)

# --- 6. PYDANTIC MODELS (for request data validation) ---
class UserCreate(BaseModel):
    fullname: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class URLRequest(BaseModel):
    url: str

# --- 7. API ENDPOINTS / ROUTES ---

# --- Homepage Endpoint ---
@app.get("/", response_class=FileResponse)
async def read_root():
    """
    This endpoint serves the main index.html file when a user
    visits the homepage (e.g., https://your-site.onrender.com/)
    """
    return "index.html"

# ===== START: NEW CODE TO FIX 404 ERRORS =====
@app.get("/{page_name}.html", response_class=FileResponse)
async def read_html_page(page_name: str):
    """
    This single route will serve any file that ends in .html
    like login.html, signup.html, info.html, etc.
    """
    return f"{page_name}.html"
# ===== END: NEW CODE =====


# --- User Registration and Login Endpoints ---
@app.post("/signup/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = models.User(fullname=user.fullname, email=user.email, hashed_password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully"}

@app.post("/token")
def login_user(form_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.email).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"message": "Login successful"}

# --- Google Authentication Routes ---
@app.get('/login')
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, str(redirect_uri))

@app.get('/auth/callback')
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/') # Redirects to the homepage

@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/') # Redirects to the homepage

# --- URL Analysis Endpoint ---
@app.post("/analyze-url/")
async def analyze_url(request: URLRequest, db: Session = Depends(get_db)):
    url_to_check = request.url
    risk_score = analyze_url_structure(url_to_check)
    
    status, verdict_class = "Safe ✅", "safe"
    if 30 <= risk_score < 60:
        status, verdict_class = "Suspicious ⚠️", "suspicious"
    elif risk_score >= 60:
        status, verdict_class = "Dangerous ❌", "dangerous"
        
    return {"url": url_to_check, "risk_score": risk_score, "status": status, "verdict_class": verdict_class}


# --- 8. HELPER FUNCTIONS ---
def analyze_url_structure(url: str) -> int:
    score = 0
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain):
        score += 30
    if len(url) > 75:
        score += 15
    shorteners = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co']
    if any(shortener in domain for shortener in shorteners):
        score += 20
    suspicious_keywords = ['login', 'secure', 'account', 'update', 'verify', 'banking', 'signin', 'password']
    if any(keyword in url.lower() for keyword in suspicious_keywords):
        score += 25
    if domain.count('.') > 2:
        score += 10
    return min(score, 100)