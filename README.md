# Tourism and Safety System 🛡️

A comprehensive tourist safety management system with real-time monitoring, SOS alerts, and administrative dashboard.

## 📋 Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Docker Installation (Recommended)](#docker-installation-recommended)
  - [Manual Installation](#manual-installation)
- [Running the Application](#running-the-application)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- 🚨 Real-time SOS Alert System
- 👤 Tourist Registration & Digital ID Cards
- 📍 Location Tracking & Safety Zones
- 👨‍💼 Administrative Dashboard
- 📊 Incident Response Management
- 🗺️ Interactive Safety Maps
- 📱 Mobile-Friendly Interface
- 🔐 Secure Authentication

## 📦 Prerequisites

### For Docker Installation:
- [Docker](https://www.docker.com/get-started) (version 20.10 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 1.29 or higher)

### For Manual Installation:
- Python 3.8 or higher
- MongoDB 4.4 or higher
- pip (Python package manager)

## 🚀 Installation Methods

### Docker Installation (Recommended)

Docker provides the easiest way to run the application with all dependencies included.

#### Step 1: Clone the Repository
```bash
git clone https://github.com/saikumarreddy2902/Toursim-and-Safety.git
cd Toursim-and-Safety
```

#### Step 2: Build and Run with Docker Compose
```bash
docker-compose up -d
```

This will:
- Build the application image
- Start MongoDB container
- Start the application container
- Set up networking between containers

#### Step 3: Access the Application
Open your browser and navigate to:
```
http://localhost:5000
```

#### Docker Management Commands

**Stop the application:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**Rebuild after code changes:**
```bash
docker-compose up -d --build
```

**Remove all containers and volumes:**
```bash
docker-compose down -v
```

### Alternative: Docker Build Only

If you prefer to use Docker without Docker Compose:

```bash
# Build the image
docker build -t tourist-safety-system .

# Run MongoDB
docker run -d --name tourist-mongo -p 27017:27017 mongo:latest

# Run the application
docker run -d --name tourist-app -p 5000:5000 --link tourist-mongo:mongo tourist-safety-system
```

## 🔧 Manual Installation

If you prefer to run without Docker:

### Step 1: Clone the Repository
```bash
git clone https://github.com/saikumarreddy2902/Toursim-and-Safety.git
cd Toursim-and-Safety
```

### Step 2: Install MongoDB

**Windows:**
- Download from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
- Run the installer and follow the setup wizard

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### Step 3: Install Python Dependencies
```bash
cd tourist-safety-system
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python host.py
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `tourist-safety-system` directory:

```env
FLASK_ENV=production
MONGODB_URI=mongodb://localhost:27017/
SECRET_KEY=your-secret-key-here
PORT=5000
```

### MongoDB Connection

The application connects to MongoDB with the following defaults:
- **Host:** localhost (or mongo container name in Docker)
- **Port:** 27017
- **Database:** tourist_safety_db

## 📱 Usage

### Admin Dashboard
- **URL:** `http://localhost:5000/admin`
- **Default Credentials:** Set up during first run

### Tourist Portal
- **URL:** `http://localhost:5000/`
- Register as a new tourist or login with existing credentials

### API Endpoints
- `/api/sos` - SOS Alert submission
- `/api/tourist/register` - Tourist registration
- `/api/admin/dashboard` - Admin statistics
- `/api/incidents` - Incident management

## 🔍 Troubleshooting

### Docker Issues

**Port already in use:**
```bash
# Change the port in docker-compose.yml
ports:
  - "8000:5000"  # Use 8000 instead of 5000
```

**Container won't start:**
```bash
# Check logs
docker-compose logs tourist-safety-app

# Restart containers
docker-compose restart
```

**Database connection failed:**
```bash
# Ensure MongoDB container is running
docker ps

# Restart MongoDB
docker-compose restart mongo
```

### Manual Installation Issues

**MongoDB not running:**
```bash
# Windows
net start MongoDB

# Linux
sudo systemctl start mongodb

# macOS
brew services start mongodb-community
```

**Port 5000 already in use:**
```bash
# Change port in host.py or use environment variable
export PORT=8000
python host.py
```

**Missing dependencies:**
```bash
pip install -r requirements.txt --upgrade
```

## 🛠️ Development

### Running in Development Mode
```bash
cd tourist-safety-system
export FLASK_ENV=development
python host.py
```

### Running Tests
```bash
python test_admin_login.py
python test_authentication.py
python comprehensive_sos_test.py
```

## 📁 Project Structure
```
Toursim-and-Safety/
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── README.md                  # This file
└── tourist-safety-system/     # Main application directory
    ├── backend/               # Backend logic
    ├── static/                # CSS, JS, images
    ├── templates/             # HTML templates
    ├── host.py                # Main application runner
    ├── requirements.txt       # Python dependencies
    └── uploads/               # User uploaded files
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is developed for educational purposes.

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Contact: saikumarreddy2902

## 🎯 Quick Start Summary

**With Docker (Recommended):**
```bash
git clone https://github.com/saikumarreddy2902/Toursim-and-Safety.git
cd Toursim-and-Safety
docker-compose up -d
# Access: http://localhost:5000
```

**Without Docker:**
```bash
git clone https://github.com/saikumarreddy2902/Toursim-and-Safety.git
cd Toursim-and-Safety/tourist-safety-system
pip install -r requirements.txt
python host.py
# Access: http://localhost:5000
```

---

Made with ❤️ for Tourist Safety