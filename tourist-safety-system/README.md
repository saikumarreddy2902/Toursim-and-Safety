# Smart Tourist Safety Monitoring System

A simple, beginner-friendly web-based prototype for monitoring tourist safety with features like digital tourist IDs, panic buttons, geo-fencing, and multilingual support.

## 🚀 Features

- **Digital Tourist ID System**: Simple registration with Aadhaar/Passport details
- **Panic Button**: Emergency alert system with GPS location tracking
- **Tourist Dashboard**: Real-time location status and safety monitoring
- **Admin Dashboard**: Monitor all tourists, alerts, and violations
- **Geo-Fencing**: Automated alerts for high-risk zones
- **Multilingual Support**: English and Hindi language options
- **Location Tracking**: Browser-based geolocation API
- **Responsive Design**: Works on desktop and mobile devices

## 📁 Project Structure

```
tourist-safety-system/
├── backend/
│   ├── app.py              # Flask application server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── static/
│   │   ├── style.css       # Main stylesheet
│   │   ├── common.js       # JavaScript utilities
│   │   └── translations.json # Language translations
│   └── templates/
│       ├── index.html      # Home page
│       ├── register.html   # Tourist registration
│       ├── tourist_dashboard.html # Tourist interface
│       └── admin_dashboard.html   # Admin interface
├── data/                   # (Legacy) No longer used; MongoDB is required
└── README.md              # This file
```

## 🛠️ Prerequisites

- **Python 3.7+** installed on your system
- **VS Code** (recommended) or any text editor
- **Web browser** with geolocation support (Chrome, Firefox, Safari, Edge)

## � Quick Start - One Command Setup

### ⚡ Instant Hosting (Recommended)

**Windows:**
```bash
# Double-click or run:
host.bat
```

**Linux/Mac:**
```bash
chmod +x host.sh
./host.sh
```

**Cross-Platform Python:**
```bash
python host.py
```

### 🎯 What You Get
- ✅ **All dependencies installed automatically**
- ✅ **Database setup and initialization**

### 1. Clone or Download the Project

If you have the project files:
- Extract them to your desired location
- Open the `tourist-safety-system` folder in your terminal/command prompt

### 2. One-Command Setup

Run the unified host manager for your platform:

**Windows Users:**
```cmd
host.bat
```

**Linux/Mac Users:**
```bash
./host.sh
```

**Any Platform (Python):**
```bash
python host.py
```

### 3. Choose Your Hosting Option

The unified host will present you with options:
1. **Quick Start** - Local development server
2. **Docker** - Containerized deployment  
3. **Heroku** - Cloud deployment
4. **Production** - Gunicorn production server
5. **Status** - Check system health
6. **Dependencies** - Install packages only
7. **Database** - Setup database only
8. **Browser** - Open application in browser
## 🌐 Access Your Application

After setup, access your Tourist Safety System at:
- **🏠 Home Page:** http://localhost:5000
- **👨‍💼 Admin Dashboard:** http://localhost:5000/admin
- **🔍 Health Check:** http://localhost:5000/health
- **📊 Reports:** http://localhost:5000/admin (admin only)

### 2. Set Up Python Environment

#### Option A: Using VS Code Terminal
1. Open VS Code terminal (`Ctrl+`` ` or `View > Terminal`)
2. Navigate to the backend directory:
   ```powershell
   cd backend
   ```

#### Option B: Using Command Prompt
1. Open Command Prompt or PowerShell
2. Navigate to the project directory:
   ```powershell
   cd path\to\tourist-safety-system\backend
   ```

### 3. Install Python Dependencies

```powershell
# Install Flask and dependencies
pip install Flask==2.3.3 Werkzeug==2.3.7

# Or install from requirements file
pip install -r requirements.txt
```

If you encounter permission issues, try:
```powershell
pip install --user -r requirements.txt
```

### 4. Run the Application

```powershell
# Make sure you're in the backend directory
python app.py
```

You should see output like:
```
 * Running on all addresses (0.0.0.0)
```

### 5. Open in Browser

1. Open your web browser
2. Go to: `http://localhost:5000` or `http://127.0.0.1:5000`
3. You should see the Tourist Safety System home page
## 🎯 How to Use

### For Tourists

1. **Register as Tourist**:
   - Click "Register Now" on the home page
   - Fill in your details (name, ID type, trip info, emergency contact)
   - Save your generated Tourist ID number

2. **Access Tourist Dashboard**:
   - Enter your Tourist ID on the home page and click "Login"
   - Allow location access when prompted
   - Use the panic button in emergencies
   - Monitor your safety status

3. **Emergency Features**:
   - **Panic Button**: Sends immediate alert with your location
   - **Location Sharing**: Share your current location
   - **Safety Status**: View if you're in a safe or danger zone

### For Administrators

1. **Access Admin Dashboard**:
   - Click "Admin Access" on the home page
   - Monitor all registered tourists
   - View panic alerts and geofence violations
   - Track tourist locations and status

2. **Admin Features**:
   - View system statistics
   - Monitor active alerts
   - Check geofence violations
   - Export tourist data

## 🌍 Language Support

- Click the language buttons (English/हिंदी) in the top-right corner
- Language preference is saved automatically
- All interface text will switch languages

## 🛡️ Safety Features

### Geo-Fencing
- Two sample high-risk zones are pre-configured
- Automatic alerts when tourists enter danger zones
- Customizable zone boundaries in `app.py`

### Location Tracking
- Automatic location updates every 5 minutes
- Manual location refresh option
- Browser-based geolocation (no GPS hardware required)

### Emergency Response
- Panic button sends immediate alerts
- Emergency contact numbers displayed
- Real-time location sharing

## 🔧 Customization

### Adding New High-Risk Zones

Edit `backend/app.py` and modify the `HIGH_RISK_ZONES` list:

```python
HIGH_RISK_ZONES = [
    {
        'name': 'Your Zone Name',
        'lat_min': 28.6000,  # Southwest corner latitude
        'lat_max': 28.6020,  # Northeast corner latitude
        'lng_min': 77.2000,  # Southwest corner longitude
        'lng_max': 77.2020   # Northeast corner longitude
    }
]
```

### Changing Emergency Numbers

Edit the emergency contacts in HTML templates or add them to the database.

### Adding New Languages

1. Add translations to `frontend/static/translations.json`
2. Add language button to templates
3. Update `switchLanguage()` function in `common.js`

## 🗃️ Database

This project now uses MongoDB only. Configure via environment variables:

- DB_BACKEND=mongo
- MONGO_URI=mongodb://localhost:27017
- MONGO_DB_NAME=tourist_safety

Collections are created automatically on first use (users, sessions, incidents, alerts, post_incident_reports, etc.).

## 🌐 API Endpoints

- `POST /api/register_tourist` - Register new tourist
- `POST /api/panic_alert` - Send panic alert
- `POST /api/update_location` - Update location
- `GET /api/tourists` - Get all tourists
- `GET /api/panic_alerts` - Get panic alerts
- `GET /api/geofence_violations` - Get violations

## 🚨 Troubleshooting

### Common Issues

1. **"Module not found" error**:
   ```powershell
   pip install Flask Werkzeug
   ```

2. **Port already in use**:
   - Close other applications using port 5000
   - Or change port in `app.py`: `app.run(port=5001)`

3. **Location not working**:
   - Ensure you're using `https://` or `localhost`
   - Allow location permissions in browser
   - Check browser console for errors

4. **Database errors (MongoDB)**:
   - Ensure MongoDB is running and reachable at your configured MONGO_URI
   - Check your .env or environment variables for MONGO_URI and MONGO_DB_NAME
   - Restart the application after updating environment variables

### Browser Compatibility

- ✅ Chrome 50+
- ✅ Firefox 40+
- ✅ Safari 10+
- ✅ Edge 15+

### Mobile Devices

- Responsive design works on all screen sizes
- Touch-friendly interface
- GPS location support on mobile browsers

## 🔒 Security Considerations

⚠️ **Important**: This is a prototype for educational purposes. For production use:

- Add user authentication and authorization
- Implement HTTPS/SSL certificates
- Use environment variables for sensitive data
- Add input validation and sanitization
- Implement proper error handling
- Use a production database (PostgreSQL, MySQL)
- Add rate limiting and CORS policies

## 📱 Future Enhancements

- Google Maps integration for visual location display
- SMS/Email notifications for emergency contacts
- Real-time chat support
- Weather and local alerts integration
- Offline mode support
- Mobile app development
- AI-powered risk assessment
- Integration with local emergency services

## 📞 Emergency Numbers (India)

- **Police**: 100
- **Ambulance**: 108
- **Fire Service**: 101
- **Tourist Helpline**: 1363

## 📝 License

This project is for educational purposes. Feel free to modify and use for learning.

## 🤝 Contributing

This is a prototype project. Suggestions for improvements:

1. Fork the project
2. Create feature branch
3. Make improvements
4. Test thoroughly
5. Submit pull request

## 📧 Support

For issues or questions:
- Check the troubleshooting section
- Review browser console for errors
- Ensure all dependencies are installed
- Verify Python and Flask versions

---

**Built with ❤️ for Smart India Hackathon 2025**

*Making tourist safety accessible and simple for everyone*