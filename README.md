# Sentinel Security: AI-Powered Insider Threat Detection System

*Last Updated: 2025-05-30*

## 🛡️ Project Overview

Sentinel Security is an advanced AI-powered insider threat detection system designed to monitor and analyze cloud environment activities in real-time. The system identifies suspicious behaviors, potential security breaches, and anomalous patterns using machine learning algorithms combined with traditional security monitoring techniques.

## 🚀 Key Features

### Real-Time Threat Detection
- **Live Monitoring Dashboard**: Real-time updates every 3-5 seconds
- **Anomaly Detection**: ML models establish baseline behavior and flag deviations
- **Pattern Recognition**: Identifies suspicious access patterns across resources
- **Contextual Analysis**: Evaluates activities within user roles and permissions

### Comprehensive Security Monitoring
- **Login Activity Tracking**: Monitor all authentication events with geolocation
- **File Activity Monitoring**: Track file access, modifications, and deletions
- **Alert Management**: Prioritized security incidents with severity levels
- **User Management**: Administrative interface for user access control
- **Threat Simulator**: Built-in simulation tool for testing and demonstrations

### Advanced Detection Capabilities
- **Geographic Anomaly Detection**: Impossible travel scenarios
- **Behavioral Analysis**: Out-of-hours activity detection
- **Privilege Escalation Monitoring**: Unusual permission changes
- **Data Exfiltration Detection**: Abnormal file download patterns
- **Brute Force Protection**: Failed login attempt recognition

## 🛠️ Technology Stack

### Backend
- **Python 3.9+** - Core programming language
- **FastAPI** - High-performance async API framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Database (easily switchable to PostgreSQL)
- **Scikit-learn** - Machine learning models
- **JWT** - Secure authentication
- **IPinfo** - Geolocation services

### Frontend
- **React 18** - Modern UI framework
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization
- **Axios** - API communication
- **React Router** - Application routing

## 📁 Project Structure

```
sentinel/
├── app/                      # Backend application
│   ├── main.py              # FastAPI application entry
│   ├── models/              # Database models
│   ├── routes/              # API endpoints
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── context/        # React context
│   │   └── api/            # API client
│   └── public/             # Static assets
├── threat_simulator.py      # Threat simulation tool
├── create_admin.py         # Admin user creation
├── clear_database.py       # Database cleanup utility
└── requirements.txt        # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sentinel
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python create_admin.py
   ```
   Default credentials: `admin@example.com` / `Admin@123`

5. **Run the backend**
   ```bash
   python run.py
   # or
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create .env file for faster development**
   ```bash
   echo "GENERATE_SOURCEMAP=false" > .env
   echo "DISABLE_ESLINT_PLUGIN=true" >> .env
   ```

4. **Start development server**
   ```bash
   npm start
   ```

   **Note**: If using WSL and experiencing slow startup, move project to Linux filesystem:
   ```bash
   cp -r /mnt/c/your/path ~/projects/sentinel
   ```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🎯 Using the Threat Simulator

The threat simulator generates realistic security events for testing and demonstration.

1. **Clear existing data (optional)**
   ```bash
   python clear_database.py
   ```

2. **Run the simulator**
   ```bash
   python threat_simulator.py
   ```

3. **Simulator Commands**
   - `start` - Begin simulation
   - `stop` - Stop simulation
   - `stats` - Show current statistics
   - `set [n]` - Set threat percentage (e.g., `set 30` for 30% threats)
   - `clear` - Clear all data
   - `help` - Show available commands
   - `exit` - Exit simulator

## 📊 Features in Detail

### Dashboard
- Real-time security metrics
- Activity charts (7-day view)
- Recent alerts with severity indicators
- System security score
- Live monitoring status

### Alerts Management
- Severity levels: Low, Medium, High, Critical
- Real-time alert updates
- Filtering by severity and status
- One-click alert resolution (admin only)

### Login Activity
- Success/failure tracking
- Geographic location mapping
- Anomaly detection indicators
- User agent analysis
- Live activity feed

### File Activity
- Action tracking (View, Download, Upload, Delete, Modify)
- Sensitive file detection
- Anomalous activity flagging
- File type categorization
- Real-time monitoring

### User Management (Admin Only)
- Create/Edit/Delete users
- Role assignment
- Department organization
- Activity status tracking
- Last login monitoring

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Role-Based Access**: Admin and user permissions
- **Password Hashing**: Bcrypt encryption
- **CORS Protection**: Configured origins
- **SQL Injection Protection**: ORM queries
- **XSS Prevention**: Input sanitization

## 🧪 Testing

### Run Backend Tests
```bash
pytest tests/
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Production Build

**Backend**:
```bash
# Use production database
export DATABASE_URL="postgresql://user:pass@host/db"
# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Frontend**:
```bash
cd frontend
npm run build
# Serve build folder with nginx or similar
```

## 🤝 Development Team

- **Lakshay Laddha** - Developer


## 📈 Future Enhancements

- [ ] Advanced ML models for better threat detection
- [ ] Integration with SIEM systems
- [ ] Automated incident response
- [ ] Multi-cloud support (AWS, Azure, GCP)
- [ ] Mobile application
- [ ] Email/SMS alerting
- [ ] Export reports (PDF/CSV)
- [ ] Dark mode UI

## 🐛 Troubleshooting

### Slow Frontend Startup (WSL)
Move project to Linux filesystem:
```bash
cp -r /mnt/c/path/to/sentinel ~/projects/
cd ~/projects/sentinel/frontend
npm start
```

### Database Connection Issues
Ensure SQLite file permissions:
```bash
chmod 664 sentinel.db
```

### Import Errors
Check Python path and virtual environment:
```bash
which python
# Should show: /path/to/sentinel/venv/bin/python
```

## 📝 License

This project is proprietary and confidential.

© 2025 Sentinel Security Team. All rights reserved.

---

For support or questions, please contact the development team.