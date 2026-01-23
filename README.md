# IEEE Paper Generator - Backend API

A robust, production-ready backend service for automated IEEE-formatted academic paper generation with custom(my own model) plagiarism detection and user authentication.

## 🎯 Project Description

This backend service powers an intelligent **IEEE Paper Generator** application designed to streamline academic paper creation. The system leverages modern AI/ML technologies to generate professionally formatted papers, detect plagiarism, and manage user authentication.

### Core Features & Tech Stack

**Backend Framework:**
- **FastAPI** - Modern, fast Python web framework with automatic API documentation
- **Uvicorn** - High-performance ASGI server

**Document Processing:**
- **python-docx** - Microsoft Word document generation
- **Pillow** - Advanced image processing
- **Matplotlib** - Formula rendering and visualization

**AI/ML & Plagiarism Detection:**
- **PyTorch** - Deep learning framework
- **Sentence-Transformers** - Semantic similarity for plagiarism detection
- **scikit-learn** - Machine learning utilities

**Database & Authentication:**
- **MongoDB** - NoSQL database for user & paper management
- **JWT-based Authentication** - Secure user sessions

**Additional Tools:**
- **Pydantic** - Data validation and serialization
- **CORS Middleware** - Cross-origin resource sharing
- **lxml** - XML/HTML parsing

## 📁 Backend Project File Structure

```
ieee_backend/
├── utils/                         # Core utility modules
│   ├── auth.py                   # User authentication & JWT handling
│   ├── ieee_generator.py         # IEEE paper generation logic
│   ├── plagiarism_checker.py     # Plagiarism detection engine
│   └── __pycache__/              # Python cache
├── tests/
│   └── test_auth_api.py          # Authentication API tests
├── images/                        # Generated images storage
├── uploads/                       # User file uploads
├── app.py                         # FastAPI main application
├── config.py                      # Configuration management
├── main.py                        # Application entry point
├── requirements_updates.txt       # Project dependencies
├── Dockerfile                     # Docker containerization
├── Procfile                       # Deployment configuration
├── test_plagiarism.py            # Plagiarism testing
├── paper_code.txt                # Sample paper data
├── sample_paper.txt              # Sample output
├── sampleFormat.txt              # Format reference
└── __pycache__/                  # Python cache
```

## 🚀 How to Run Backend

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- MongoDB (local or cloud - Atlas)
- Virtual environment (recommended)

### Installation & Setup

**Step 1: Create Virtual Environment**
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Step 2: Install Dependencies**
```bash
pip install -r requirements_updates.txt
```

**Step 3: Configure Environment Variables**
Create a `.env` file in the project root:
```env
MONGO_URI=mongodb://localhost:27017/ieee_papers
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Step 4: Start the Backend Server**
```bash
# Using Uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Or using Python main.py (if configured)
python main.py
```

**Step 5: Access API Documentation**
- Open your browser and navigate to: `http://localhost:8000/docs`
- Interactive Swagger UI will display all available endpoints

## 📊 API Endpoints Overview

**Authentication:**
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/verify` - Token verification

**Paper Generation:**
- `POST /generate/paper` - Generate IEEE formatted paper
- `GET /papers/{paper_id}` - Retrieve paper

**Plagiarism Detection:**
- `POST /plagiarism/check` - Analyze plagiarism score
- `POST /plagiarism/upload` - Upload file for analysis

**File Management:**
- `POST /upload/image` - Upload images
- `GET /download/{file_id}` - Download generated documents

## 🛠️ Development Commands

**Install new package:**
```bash
pip install package_name
pip freeze > requirements_updates.txt
```

## 🔒 Security Features

✅ JWT-based authentication
✅ CORS protection
✅ Input validation with Pydantic
✅ Environment variable configuration
✅ Secure file upload handling
✅ MongoDB connection security

## 🎓 Professional Summary

This backend demonstrates proficiency in:

- **Modern API Development** - FastAPI with async/await patterns
- **AI/ML Integration** - Sentence transformers for intelligent plagiarism detection
- **Database Design** - MongoDB schema optimization
- **Security** - JWT authentication, CORS, data validation
- **Code Quality** - Modular architecture, comprehensive error handling
- **Testing** - Unit and integration tests
- **Production Readiness** - Error logging, CORS middleware, scalable design

---

**Thank you for exploring this project! This IEEE Paper Generator Backend showcases modern software engineering practices, from AI-powered document processing to enterprise-grade API design. We believe this project demonstrates the technical depth and practical application knowledge valuable to innovative tech teams. 🚀**

**For Recruiters:** This project exemplifies full-stack backend development, demonstrating expertise in FastAPI, machine learning integration, database management, and production-ready application architecture.
