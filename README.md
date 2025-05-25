# Sentinel Security: AI Insider Threat Detection for Cloud

*Last Updated: 2025-05-25 18:38:42*

## Project Overview

Sentinel Security is an advanced AI-powered insider threat detection system designed to monitor and analyze cloud environment activities to identify suspicious behaviors and potential security breaches. The system combines machine learning algorithms with traditional security monitoring techniques to provide a comprehensive security solution for organizations using cloud services.

The project implements a modern full-stack architecture with a Python FastAPI backend powering the AI threat detection engine and a React frontend providing an intuitive security monitoring dashboard.

## Development Team

- Lakshay Laddha(Lead Developer)
- Harsh PS, Piyush Kumar

## Technology Stack

### Backend Technologies
- **Python 3.9+**: Core programming language
- **FastAPI**: High-performance API framework
- **SQLAlchemy**: ORM for database interactions
- **Pydantic**: Data validation and settings management
- **SQLite**: Database for storing user data, alerts, and activity logs
- **Scikit-learn/TensorFlow**: For AI models that detect anomalous behaviors
- **JWT Authentication**: For secure user authentication
- **Geolocation Services**: For tracking login locations and detecting geographic anomalies

### Frontend Technologies
- **React 18**: JavaScript library for building the user interface
- **TypeScript**: For type-safe code
- **Material-UI**: Component library for consistent UI design
- **Chart.js**: For data visualization dashboards
- **React Router**: For application navigation
- **Axios**: For API communication with the backend
- **TailwindCSS**: For utility-first CSS styling

## Key Features

### AI-Powered Threat Detection
- **Anomaly Detection**: Machine learning models that establish baseline user behavior and flag deviations
- **Pattern Recognition**: Identification of suspicious access patterns across cloud resources
- **Contextual Analysis**: Evaluation of activities within the context of user roles and permissions

### Comprehensive Security Dashboard
- **Overview Dashboard**: Real-time visualization of security posture
- **Security Alerts**: Prioritized list of potential security incidents
- **Login Activity Monitoring**: Tracking of all authentication events
- **File Activity Tracking**: Monitoring of sensitive file access and modifications
- **User Management**: Administrative interface for managing system users
- **Settings**: Configurable security parameters and notification preferences

### Advanced Security Monitoring
- **Geographic Login Analysis**: Detection of impossible travel scenarios
- **Out-of-hours Activity Detection**: Flagging activities occurring outside normal working hours
- **Privilege Escalation Monitoring**: Detection of unusual permission changes
- **Data Exfiltration Detection**: Identification of unusual file download patterns
- **Brute Force Attack Detection**: Recognition of repeated failed login attempts

## Project Structure


## Installation

### Backend Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

2. Install dependencies:
   pip install -r requirements.txt
   
3. Initialize the database:
   python setup.py
   
4. Create an admin user:
   python create_admin.py

5. Run the backend server:
   python run.py

### Frontend Setup

1. Navigate to the frontend directory:
   cd frontend

2. Install dependencies:
   npm install

3. Start the development server:
   npm start


### Demo & Usage
1. Access the web interface at http://localhost:3000
2. Log in with your admin credentials
3. Navigate the dashboard to monitor security alerts, login activities, and file access events
4. For demonstration purposes, you can use the threat simulator:

   python threat_simulator.py --events 50

### Future Enhancements

Advanced AI Models for better threat detection
Integration with SIEM Systems
Automated Response Actions
Expanded Cloud Coverage for additional providers
Mobile Application for on-the-go monitoring

### License
This project is proprietary and confidential.

© 2025 Sentinel Security Team. All rights reserved.
