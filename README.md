# AI-Based Insider Threat Detection in Cloud Environments

![Insider Threat Detection Dashboard](docs/images/dashboard.png)

## Overview

This project implements an AI-powered system that detects potential insider threats in cloud environments (AWS, Azure, etc.) by analyzing activity logs and identifying anomalous patterns. The system uses machine learning to score activities in real-time and provides a dashboard for security teams to monitor and respond to threats.

## Key Features

- **Log Simulation**: Generate realistic cloud activity logs with users, actions, timestamps, and IP addresses
- **GeoIP Resolution**: Enrich logs with geolocation data based on IP addresses
- **Feature Engineering**: Extract 20+ behavioral features from raw logs
- **Anomaly Detection**: ML model (Isolation Forest) to identify outlier behavior
- **REST API**: Real-time threat scoring API with FastAPI
- **Interactive Dashboard**: React.js frontend with threat visualizations and filtering
- **Docker Deployment**: One-command setup with Docker Compose

## Architecture

The system is composed of several modules that work together:

1. **Data Ingestion**: Simulates realistic cloud activity logs
2. **Preprocessing**: Transforms raw logs into ML-ready features
3. **ML Model**: Detects anomalies using Isolation Forest
4. **API Service**: FastAPI service for real-time threat detection
5. **Dashboard**: React frontend for visualizing threats

![Architecture Diagram](docs/images/architecture.png)

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for development without Docker)
- Node.js 14+ (for frontend development without Docker)

### Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cloud-insider-threat-ai.git
   cd cloud-insider-threat-ai