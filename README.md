# Sentinel: Security Monitoring and Threat Detection API

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0-green)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)

Sentinel is a comprehensive security monitoring and threat detection system designed to track user activities, detect suspicious behavior, and alert administrators to potential security threats.

## Features

- **User Authentication**: Secure JWT-based authentication system with role-based access control
- **Activity Monitoring**: Track login attempts and file operations
- **Geolocation Tracking**: Record and analyze login locations for suspicious patterns
- **Threat Detection**: Automatic detection of unusual user behavior
- **Alert System**: Real-time notifications for suspicious activities
- **Dashboard**: Comprehensive overview of system security status
- **Admin Controls**: User management and security configuration

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL (or SQLite for development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sentinel.git
   cd sentinel
Create and activate a virtual environment:

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
pip install -r requirements.txt
Set up environment variables:

bash
cp .env.example .env
# Edit .env with your settings
Run database migrations:

bash
alembic upgrade head
Start the development server:

bash
uvicorn app.main:app --reload
Docker Setup
Alternatively, use Docker Compose:

bash
docker-compose up -d
API Endpoints
Authentication
POST /api/v1/login - Obtain access token
POST /api/v1/logout - End user session
Users
GET /api/v1/users/ - List all users (admin)
POST /api/v1/users/ - Create new user (admin)
GET /api/v1/users/me - Get current user info
GET /api/v1/users/{user_id} - Get specific user info
PUT /api/v1/users/{user_id} - Update user details
DELETE /api/v1/users/{user_id} - Remove user (admin)
Activities
GET /api/v1/activities/logins - List login activities
POST /api/v1/activities/logins - Record new login manually
GET /api/v1/activities/files - List file activities
POST /api/v1/activities/files - Record file activity
POST /api/v1/activities/file - Simplified file activity recording
GET /api/v1/activities/alerts - List security alerts
POST /api/v1/activities/alerts - Create new security alert
PUT /api/v1/activities/alerts/{alert_id} - Update alert status
Dashboard
GET /api/v1/dashboard - Get security overview data
Health Check
GET /health - Check service health
Project Structure
Code
sentinel/
├── app/
│   ├── core/             # Core configuration
│   ├── models/           # Database models
│   ├── routes/           # API routes
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic services
│   ├── utils/            # Utility functions
│   ├── database.py       # Database connection
│   └── main.py           # FastAPI application
├── migrations/           # Alembic migrations
├── tests/                # Test suite
├── docker/               # Docker configuration
├── .env.example          # Environment variables template
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
└── README.md             # This file
Technologies Used
FastAPI: High-performance API framework
SQLAlchemy: SQL toolkit and ORM
Pydantic: Data validation and settings management
Alembic: Database migrations
PyJWT: JSON Web Token implementation
Passlib: Password hashing utilities
Pytest: Testing framework
Development
Running Tests
bash
pytest
Creating Migrations
bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
License
MIT License

Last Updated
2025-05-13