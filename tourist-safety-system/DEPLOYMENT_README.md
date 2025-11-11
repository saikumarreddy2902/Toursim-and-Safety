# 🚀 Tourist Safety System - Complete Hosting Guide

## 📋 Quick Start (Local Development)

```bash
# 1. Navigate to project directory
cd tourist-safety-system

# 2. Run deployment script
./deploy.bat local          # Windows
./deploy.sh local           # Linux/Mac

# 3. Access the application
# Open http://localhost:5000 in your browser
```

## 🌐 Production Hosting Options

### 1. 🔥 Heroku (Recommended for beginners)

**Prerequisites:**
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- Git repository

**Deploy:**
```bash
# Quick deploy (automated)
./deploy.sh heroku

# Or manual steps:
heroku login
heroku create your-app-name
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
git push heroku main
```

**Access:** `https://your-app-name.herokuapp.com`

### 2. 🐳 Docker (Recommended for production)

**Prerequisites:**
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

**Deploy:**
```bash
# Quick deploy
./deploy.sh docker

# Or using Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

**Access:** `http://localhost:5000`

### 3. ☁️ DigitalOcean/AWS/Google Cloud

**1. Create a Droplet/Instance**
```bash
# Ubuntu 20.04 LTS recommended
apt update && apt upgrade -y
apt install python3 python3-pip nginx -y
```

**2. Clone and Setup**
```bash
git clone <your-repo-url>
cd tourist-safety-system
pip3 install -r backend/requirements.txt
```

**3. Configure Nginx**
```bash
sudo cp nginx.conf /etc/nginx/sites-available/tourist-safety
sudo ln -s /etc/nginx/sites-available/tourist-safety /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

**4. Run with Gunicorn**
```bash
cd backend
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

### 4. 📱 PythonAnywhere (Beginner-friendly)

**Steps:**
1. Upload files to PythonAnywhere
2. Create a new Flask web app
3. Edit WSGI configuration file:
```python
import sys
path = '/home/yourusername/tourist-safety-system/backend'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```
4. Configure static files mapping
5. Reload web app

### 5. 🌟 Vercel (Serverless)

**Deploy:**
```bash
npm install -g vercel
vercel --prod
```

**Note:** Requires converting Flask routes to Vercel serverless functions.

## 🔒 Production Security Checklist

### Essential Security Steps:
- [ ] Change default admin password
- [ ] Set secure `SECRET_KEY` environment variable
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure firewall (only allow ports 80, 443, 22)
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Enable rate limiting
- [ ] Update all dependencies

### Environment Variables:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-super-secret-key-here
export ADMIN_PASSWORD=secure-admin-password
export DATABASE_URL=sqlite:///data/tourist_safety.db
```

## 📊 Monitoring and Maintenance

### Health Checks:
```bash
# Check if app is running
curl http://localhost:5000/health

# View logs
tail -f logs/app.log

# Monitor resource usage
htop
```

### Database Backup:
```bash
# Backup SQLite database
cp data/tourist_safety.db backups/backup_$(date +%Y%m%d_%H%M%S).db

# Automated backup script
0 2 * * * /path/to/backup_script.sh
```

## 🚨 Troubleshooting

### Common Issues:

**Port already in use:**
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

**Permission denied:**
```bash
# Fix file permissions
chmod +x deploy.sh
chmod 755 backend/
```

**Module not found:**
```bash
# Install missing dependencies
pip install -r backend/requirements.txt
```

**Database errors:**
```bash
# Reset database
rm data/tourist_safety.db
python backend/app.py  # Will recreate database
```

## 📞 Support and Documentation

### API Endpoints:
- `GET /` - Home page
- `GET /admin` - Admin dashboard
- `POST /api/sos` - Emergency alerts (requires authentication)
- `GET /api/reports` - Incident reports (admin only)
- `GET /health` - Health check

### Architecture:
- **Backend:** Flask (Python)
- **Frontend:** HTML/CSS/JavaScript
- **Database:** SQLite (production: PostgreSQL recommended)
- **Authentication:** Session-based
- **Real-time:** WebSocket connections

### Performance Tips:
- Use Redis for session storage in production
- Implement database connection pooling
- Enable gzip compression
- Use CDN for static assets
- Configure caching headers

---

## 🎯 Quick Deployment Commands

```bash
# Local development
./deploy.bat local

# Docker deployment
docker-compose up -d

# Heroku deployment
git push heroku main

# Production with Gunicorn
gunicorn --bind 0.0.0.0:5000 backend.wsgi:app
```

**🌐 Live Demo:** [Add your hosted URL here]

**📧 Support:** [Your contact information]

---

*Last updated: September 14, 2025*