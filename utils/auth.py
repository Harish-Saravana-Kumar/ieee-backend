from datetime import datetime, timedelta
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pydantic import BaseModel, EmailStr
import jwt
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
MONGODB_URL = "mongodb+srv://malarharish007_db_user:niFy0jtVgiiRIqde@cluster0.jtf357u.mongodb.net/?appName=Cluster0"
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

try:
    client = MongoClient(MONGODB_URL)
    db = client["ieee_db"]
    users_collection = db["users"]
    
    # Create unique index on email
    users_collection.create_index("email", unique=True)
except Exception as e:
    print(f"MongoDB Connection Error: {e}")

# --------- Pydantic Models ---------

class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[dict] = None

class LogoutRequest(BaseModel):
    token: str

# --------- Blacklist for Logged Out Tokens ---------
# In production, use Redis for better performance
token_blacklist = set()

# --------- Password Hashing ---------

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# --------- JWT Token Handling ---------

def create_access_token(user_id: str) -> str:
    """Create JWT access token"""
    payload = {
        "user_id": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return user_id"""
    try:
        # Check if token is blacklisted
        if token in token_blacklist:
            return None
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# --------- Database Operations ---------

def create_user(email: str, password: str, full_name: str) -> dict:
    """Create a new user in MongoDB"""
    try:
        hashed_password = hash_password(password)
        user_data = {
            "email": email,
            "password": hashed_password,
            "full_name": full_name,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = users_collection.insert_one(user_data)
        user_data["_id"] = str(result.inserted_id)
        return user_data
    except DuplicateKeyError:
        raise ValueError("Email already registered")
    except Exception as e:
        raise Exception(f"Error creating user: {str(e)}")

def get_user_by_email(email: str) -> Optional[dict]:
    """Get user from MongoDB by email"""
    try:
        user = users_collection.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        print(f"Error fetching user: {str(e)}")
        return None

def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user from MongoDB by ID"""
    try:
        from bson.objectid import ObjectId
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        print(f"Error fetching user: {str(e)}")
        return None

# --------- Authentication Logic ---------

def signup_user(email: str, password: str, full_name: str) -> tuple[bool, str, Optional[str], Optional[dict]]:
    """Handle user signup"""
    try:
        # Validate input
        if not email or not password or not full_name:
            return False, "All fields are required", None, None
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters", None, None
        
        # Check if user exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return False, "Email already registered", None, None
        
        # Create user
        user = create_user(email, password, full_name)
        
        # Generate token
        token = create_access_token(str(user.get("_id")))
        
        # Return user data without password
        user_data = {
            "id": user.get("_id"),
            "email": user.get("email"),
            "full_name": user.get("full_name")
        }
        
        return True, "Signup successful", token, user_data
    
    except ValueError as e:
        return False, str(e), None, None
    except Exception as e:
        return False, f"Signup error: {str(e)}", None, None

def login_user(email: str, password: str) -> tuple[bool, str, Optional[str], Optional[dict]]:
    """Handle user login"""
    try:
        # Validate input
        if not email or not password:
            return False, "Email and password are required", None, None
        
        # Get user
        user = get_user_by_email(email)
        if not user:
            return False, "Invalid email or password", None, None
        
        # Verify password
        if not verify_password(password, user.get("password", "")):
            return False, "Invalid email or password", None, None
        
        # Generate token
        token = create_access_token(str(user.get("_id")))
        
        # Return user data without password
        user_data = {
            "id": user.get("_id"),
            "email": user.get("email"),
            "full_name": user.get("full_name")
        }
        
        return True, "Login successful", token, user_data
    
    except Exception as e:
        return False, f"Login error: {str(e)}", None, None

def logout_user(token: str) -> tuple[bool, str]:
    """Handle user logout by blacklisting token"""
    try:
        if token in token_blacklist:
            return False, "Token already logged out"
        
        token_blacklist.add(token)
        return True, "Logout successful"
    except Exception as e:
        return False, f"Logout error: {str(e)}"
